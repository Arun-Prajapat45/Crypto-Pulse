from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from ..models import UserCreate, UserLogin, UserPublic, TokenResponse, GoogleAuthPayload, ChangePasswordRequest, ForgotPasswordRequest
from ..auth import hash_password, verify_password, create_access_token
from ..db import get_db
from ..deps import get_current_user
from ..config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserPublic)
async def signup(payload: UserCreate, db=Depends(get_db)):
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    doc = {
        "username": payload.username,
        "email": payload.email,
        "password_hash": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc),
        "profile_photo": None,
        "auth_provider": "local",
    }
    res = await db.users.insert_one(doc)
    doc["_id"] = res.inserted_id
    return UserPublic(**doc)


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, db=Depends(get_db), settings=Depends(get_settings)):
    user = await db.users.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user.get("password_hash", "")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token, expire, jti = create_access_token(str(user["_id"]))
    await db.sessions.insert_one({"user_id": user["_id"], "jti": jti, "expires_at": expire})
    # Update last login time
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login_at": datetime.now(timezone.utc)}}
    )
    return TokenResponse(access_token=token, expires_in=settings.jwt_exp_hours * 3600)



@router.post("/google", response_model=TokenResponse)
async def google_auth(payload: GoogleAuthPayload, db=Depends(get_db), settings=Depends(get_settings)):
    """Authenticate with Google OAuth"""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured"
        )
    
    try:
        # Verify the Google ID token with clock skew tolerance
        # This handles minor time differences between client and server (up to 10 seconds)
        idinfo = id_token.verify_oauth2_token(
            payload.credential,
            google_requests.Request(),
            settings.google_client_id,
            clock_skew_in_seconds=10  # Allow 10 seconds of clock difference
        )
        
        # Get user info from the token
        email = idinfo.get("email")
        name = idinfo.get("name", email.split("@")[0])
        picture = idinfo.get("picture")
        google_id = idinfo.get("sub")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        # Check if user exists
        user = await db.users.find_one({"email": email})
        
        if user:
            # Update Google info if user exists
            # Always update profile_photo to match current Google picture 
            # (even if None - this handles cases where Google picture becomes unavailable)
            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": {
                    "google_id": google_id,
                    "profile_photo": picture,  # Always update to current Google picture
                    "auth_provider": user.get("auth_provider", "google"),
                    "last_login_at": datetime.now(timezone.utc)
                }}
            )
        else:
            # Create new user with Google info
            doc = {
                "username": name,
                "email": email,
                "password_hash": "",  # No password for Google auth users
                "created_at": datetime.now(timezone.utc),
                "profile_photo": picture,
                "google_id": google_id,
                "auth_provider": "google",
            }
            res = await db.users.insert_one(doc)
            user = doc
            user["_id"] = res.inserted_id
        
        # Create session token
        token, expire, jti = create_access_token(str(user["_id"]))
        await db.sessions.insert_one({"user_id": user["_id"], "jti": jti, "expires_at": expire})
        
        return TokenResponse(access_token=token, expires_in=settings.jwt_exp_hours * 3600)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )


@router.post("/logout")
async def logout(current=Depends(get_current_user), db=Depends(get_db)):
    # revoke all active sessions for this user (simple strategy)
    await db.revoked_tokens.insert_many(
        [{"jti": s["jti"], "revoked_at": datetime.now(timezone.utc)} async for s in db.sessions.find({"user_id": current["_id"]})]
    )
    await db.sessions.delete_many({"user_id": current["_id"]})
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserPublic)
async def me(current=Depends(get_current_user)):
    # Check if there's a profile photo in JSON fallback (for when DB doesn't update)
    from pathlib import Path
    import json
    
    user_id_str = str(current["_id"])
    profile_photos_json = Path(__file__).resolve().parent.parent / "profilephotos" / "profile_photos.json"
    
    if not current.get("profile_photo") and profile_photos_json.exists():
        try:
            with open(profile_photos_json, "r") as f:
                photos_data = json.load(f)
                if user_id_str in photos_data:
                    current["profile_photo"] = photos_data[user_id_str]
        except Exception:
            pass
    
    return UserPublic(**current)


@router.post("/change-password")
async def change_password(payload: ChangePasswordRequest, current=Depends(get_current_user), db=Depends(get_db)):
    """Change the user's password"""
    # Check if user is using Google auth (no password to verify)
    if current.get("auth_provider") == "google" and not current.get("password_hash"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for Google-authenticated accounts"
        )
    
    # Verify current password
    if not verify_password(payload.current_password, current.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Validate new password
    if len(payload.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters"
        )
    
    # Update password
    new_hash = hash_password(payload.new_password)
    await db.users.update_one(
        {"_id": current["_id"]},
        {"$set": {"password_hash": new_hash}}
    )
    
    return {"detail": "Password changed successfully"}


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest, db=Depends(get_db), settings=Depends(get_settings)):
    """Send password reset email with secure token
    
    This endpoint:
    1. Checks if the email exists in the database
    2. Generates a secure reset token
    3. Stores the token with 1-hour expiration
    4. Sends an email with the reset link
    """
    from ..services.email_service import generate_reset_token, send_password_reset_email
    
    # Check if user exists
    user = await db.users.find_one({"email": payload.email})
    
    # Always return success to prevent email enumeration attacks
    # But only send email if user actually exists
    if user:
        # Generate secure reset token
        reset_token = generate_reset_token()
        
        # Store token in database with 1-hour expiration
        await db.password_resets.insert_one({
            "email": payload.email,
            "token": reset_token,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            "used": False
        })
        
        # Send email (async in background would be better in production)
        try:
            await send_password_reset_email(payload.email, reset_token, settings)
        except Exception as e:
            print(f"Error sending email: {e}")
            # Don't expose email sending errors to prevent information leakage
    
    return {
        "detail": "If an account with that email exists, password reset instructions have been sent."
    }


@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db=Depends(get_db)
):
    """Reset password using the token from email
    
    This endpoint:
    1. Validates the reset token
    2. Checks if it's not expired or already used
    3. Updates the user's password
    4. Marks the token as used
    """
    # Find the reset token
    reset_request = await db.password_resets.find_one({
        "token": token,
        "used": False,
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not reset_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Validate new password
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )
    
    # Update user's password
    new_hash = hash_password(new_password)
    await db.users.update_one(
        {"email": reset_request["email"]},
        {"$set": {"password_hash": new_hash}}
    )
    
    # Mark token as used
    await db.password_resets.update_one(
        {"_id": reset_request["_id"]},
        {"$set": {"used": True, "used_at": datetime.now(timezone.utc)}}
    )
    
    return {"detail": "Password has been reset successfully. You can now log in with your new password."}


@router.get("/google-client-id")
async def get_google_client_id(settings=Depends(get_settings)):
    """Get the Google Client ID for frontend OAuth"""
    if not settings.google_client_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google OAuth not configured"
        )
    return {"client_id": settings.google_client_id}
