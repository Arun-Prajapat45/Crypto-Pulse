"""
Email service for sending password reset emails
"""
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from ..config import Settings


def generate_reset_token():
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)


async def send_password_reset_email(
    to_email: str,
    reset_token: str,
    settings: Settings
):
    """
    Send password reset email with reset link
    
    Args:
        to_email: Recipient email address
        reset_token: Password reset token
        settings: Application settings
    """
    # Skip if SMTP is not configured
    if not settings.smtp_username or not settings.smtp_password:
        print(f"⚠️  Email not sent: SMTP not configured. Reset token: {reset_token}")
        return False
    
    try:
        # Create reset link
        reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"
        
        # Email content
        subject = "Password Reset Request - CryptoPulse"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; background-color: #0a0f1a; color: #e2e8f0; margin: 0; padding: 0;">
            <div style="max-width: 600px; margin: 40px auto; background: #1a1f35; border-radius: 16px; border: 1px solid rgba(16, 185, 129, 0.2); overflow: hidden;">
                <div style="background: linear-gradient(90deg, #10b981 0%, #059669 100%); padding: 30px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">🔐 CryptoPulse</h1>
                    <p style="margin: 10px 0 0 0; color: rgba(255, 255, 255, 0.9);">Password Reset Request</p>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #10b981; font-size: 22px; margin-bottom: 20px;">Reset Your Password</h2>
                    <p style="color: #cbd5e1; line-height: 1.6; margin-bottom: 20px;">Hello,</p>
                    <p style="color: #cbd5e1; line-height: 1.6; margin-bottom: 20px;">We received a request to reset your password for your CryptoPulse account. Click the button below to create a new password:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="display: inline-block; background: linear-gradient(90deg, #10b981 0%, #059669 100%); color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: bold;">Reset Password</a>
                    </div>
                    
                    <div style="background-color: rgba(59, 130, 246, 0.15); border-left: 4px solid #3b82f6; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="color: #93c5fd; margin: 0; line-height: 1.6;">
                            <strong style="color: #60a5fa;">ℹ️ Important:</strong> This link will expire in <strong style="color: #60a5fa;">1 hour</strong> for security reasons.
                        </p>
                    </div>
                    
                    <p style="color: #cbd5e1; line-height: 1.6; margin-bottom: 10px;">If the button doesn't work, copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #10b981; font-size: 14px; background-color: rgba(16, 185, 129, 0.1); padding: 10px; border-radius: 4px; margin-bottom: 20px;">{reset_link}</p>
                    
                    <div style="background-color: rgba(239, 68, 68, 0.15); border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; border-radius: 4px;">
                        <p style="color: #fca5a5; margin: 0; line-height: 1.6;">
                            <strong style="color: #f87171;">⚠️ Security Notice:</strong> If you didn't request this password reset, please ignore this email. Your account remains secure.
                        </p>
                    </div>
                    
                    <p style="color: #cbd5e1; line-height: 1.6; margin-top: 30px;">Best regards,<br><strong style="color: #10b981;">The CryptoPulse Team</strong></p>
                </div>
                <div style="background: #0a0f1a; padding: 20px; text-align: center; color: #64748b; font-size: 12px; border-top: 1px solid rgba(255, 255, 255, 0.05);">
                    <p style="margin: 0 0 10px 0;">© 2026 CryptoPulse - AI-Powered Cryptocurrency Forecasting</p>
                    <p style="margin: 0; color: #475569;">This is an automated email. Please do not reply to this message.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        text_body = f"""
        Password Reset Request - CryptoPulse
        
        Hello,
        
        We received a request to reset your password for your CryptoPulse account.
        
        Click the link below to create a new password:
        {reset_link}
        
        This link will expire in 1 hour for security reasons.
        
        If you didn't request this password reset, please ignore this email.
        
        Best regards,
        The CryptoPulse Team
        
        © 2026 CryptoPulse - AI-Powered Cryptocurrency Forecasting
        """
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.smtp_from_email or settings.smtp_username
        message["To"] = to_email
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, "plain")
        part2 = MIMEText(html_body, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(message)
        
        print(f"✅ Password reset email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {str(e)}")
        return False
