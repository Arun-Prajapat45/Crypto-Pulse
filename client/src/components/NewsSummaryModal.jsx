import { useState, useEffect, useRef } from "react";
import PropTypes from "prop-types";
import { api } from "../services/api";

const NewsSummaryModal = ({ news, isOpen, onClose }) => {
    const [messages, setMessages] = useState([]);
    const [displayedMessages, setDisplayedMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [userInput, setUserInput] = useState("");
    const [isSending, setIsSending] = useState(false);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Scroll to bottom when messages change
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [displayedMessages]);

    // Fetch initial summary when modal opens
    useEffect(() => {
        if (isOpen && news) {
            fetchInitialSummary();
        } else {
            // Reset state when modal closes
            setMessages([]);
            setDisplayedMessages([]);
            setError(null);
            setUserInput("");
        }
    }, [isOpen, news]);

    // Animate messages character by character
    useEffect(() => {
        if (messages.length === 0) return;

        const lastMessage = messages[messages.length - 1];
        const lastDisplayed = displayedMessages[displayedMessages.length - 1];

        // Check if we need to animate a new message
        if (!lastDisplayed || lastMessage.id !== lastDisplayed.id || lastMessage.content !== lastDisplayed.content) {
            if (lastMessage.role === "assistant") {
                animateMessage(lastMessage);
            } else {
                // User messages appear instantly
                setDisplayedMessages([...messages]);
            }
        }
    }, [messages]);

    const animateMessage = (message) => {
        let currentIndex = 0;
        const fullText = message.content;

        // Start with all previous messages plus empty current message
        const previousMessages = messages.slice(0, -1);

        const interval = setInterval(() => {
            if (currentIndex <= fullText.length) {
                const partialMessage = {
                    ...message,
                    content: fullText.substring(0, currentIndex),
                    isAnimating: currentIndex < fullText.length
                };
                setDisplayedMessages([...previousMessages, partialMessage]);
                currentIndex += 2; // 2 characters at a time for faster animation
            } else {
                clearInterval(interval);
            }
        }, 15);
    };

    const fetchInitialSummary = async () => {
        setLoading(true);
        setError(null);

        // Add user's initial request
        const userMessage = {
            id: Date.now(),
            role: "user",
            content: "Analyze this article for me with summary, sentiment analysis, and price impact"
        };

        setMessages([userMessage]);
        setDisplayedMessages([userMessage]);

        try {
            const res = await api.post("/news/summarize", {
                title: news.title,
                body: news.body,
                url: news.url,
            });

            const data = res.data || {};

            const assistantMessage = {
                id: Date.now() + 1,
                role: "assistant",
                content: data.summary || "",
            };

            setMessages([userMessage, assistantMessage]);
        } catch (err) {
            const status = err.response?.status;
            const detail = err.response?.data?.detail;
            let message = "Failed to generate summary";
            if (status === 404) {
                message = "Summary service unavailable. Ensure the backend server is running.";
            } else if (typeof detail === "string") {
                message = detail;
            } else if (err.message) {
                message = err.message;
            }
            setError(message);
        } finally {
            setLoading(false);
        }
    };

    const sendMessage = async (messageText) => {
        if (!messageText.trim() || isSending) return;

        setIsSending(true);
        setError(null);

        // Add user message
        const userMessage = {
            id: Date.now(),
            role: "user",
            content: messageText
        };

        const updatedMessages = [...messages, userMessage];
        setMessages(updatedMessages);
        setDisplayedMessages(updatedMessages);
        setUserInput("");

        try {
            // Prepare conversation history (exclude the current message)
            const conversationHistory = messages.map(msg => ({
                role: msg.role,
                content: msg.content
            }));

            const res = await api.post("/news/chat", {
                title: news.title,
                body: news.body,
                message: messageText,
                conversation_history: conversationHistory,
                sentiment: news.sentiment,
            });

            const data = res.data || {};

            const assistantMessage = {
                id: Date.now() + 1,
                role: "assistant",
                content: data.response || "",
            };

            setMessages([...updatedMessages, assistantMessage]);
        } catch (err) {
            const status = err.response?.status;
            const detail = err.response?.data?.detail;
            let message = "Failed to get response";
            if (status === 404) {
                message = "Chat service unavailable. Ensure the backend server is running.";
            } else if (typeof detail === "string") {
                message = detail;
            } else if (err.message) {
                message = err.message;
            }
            setError(message);
        } finally {
            setIsSending(false);
        }
    };

    const handleSend = () => {
        sendMessage(userInput);
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleQuickAction = (action) => {
        const quickQuestions = {
            sentiment: "Why does this article have this sentiment? Explain in detail.",
            price: "What will be the price impact? Provide detailed analysis.",
            details: "Can you explain this in more detail with specific examples?"
        };
        sendMessage(quickQuestions[action]);
    };

    const handleBackdropClick = (e) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    if (!isOpen) return null;

    return (
        <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in"
            onClick={handleBackdropClick}
        >
            <div className="glass rounded-2xl border border-white/10 max-w-3xl w-full max-h-[85vh] overflow-hidden shadow-2xl animate-scale-in flex flex-col">
                {/* Header */}
                <div className="border-b border-white/10 p-5 flex items-start justify-between flex-shrink-0">
                    <div className="flex-1 pr-4">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent/20 to-emerald-500/20 flex items-center justify-center">
                                <svg className="w-4 h-4 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                                </svg>
                            </div>
                            <h3 className="text-sm font-semibold text-accent">AI News Analyst</h3>
                        </div>
                        <p className="text-sm text-white font-medium line-clamp-2">{news?.title}</p>
                    </div>
                    <button
                        onClick={onClose}
                        className="flex-shrink-0 w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center transition-colors"
                    >
                        <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Messages area */}
                <div className="flex-1 overflow-y-auto p-5 space-y-4" style={{ minHeight: '400px', maxHeight: '50vh' }}>
                    {displayedMessages.map((msg) => (
                        <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[85%] ${msg.role === 'user'
                                    ? 'bg-accent/10 border border-accent/20 rounded-2xl rounded-tr-sm'
                                    : 'bg-white/5 border border-white/10 rounded-2xl rounded-tl-sm'
                                } px-4 py-3`}>
                                <p className="text-sm text-slate-200 whitespace-pre-wrap leading-relaxed">
                                    {msg.content}
                                    {msg.isAnimating && <span className="inline-block w-0.5 h-4 bg-accent ml-0.5 animate-pulse"></span>}
                                </p>
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div className="flex justify-start">
                            <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-sm px-4 py-3">
                                <div className="flex items-center gap-2">
                                    <div className="flex gap-1">
                                        <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                        <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                        <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                    </div>
                                    <span className="text-sm text-slate-400">Analyzing...</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {error && (
                        <div className="flex justify-start">
                            <div className="bg-rose-500/10 border border-rose-500/30 rounded-2xl px-4 py-3 max-w-[85%]">
                                <div className="flex items-start gap-2">
                                    <svg className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                    <p className="text-sm text-rose-400">{error}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Quick Actions */}
                {messages.length > 0 && !loading && !isSending && (
                    <div className="px-5 pb-3 flex flex-wrap gap-2">
                        <button
                            onClick={() => handleQuickAction('sentiment')}
                            className="px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-xs text-slate-300 transition-colors flex items-center gap-1.5"
                        >
                            <span>💭</span> Explain Sentiment
                        </button>
                        <button
                            onClick={() => handleQuickAction('price')}
                            className="px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-xs text-slate-300 transition-colors flex items-center gap-1.5"
                        >
                            <span>📊</span> Price Impact
                        </button>
                        <button
                            onClick={() => handleQuickAction('details')}
                            className="px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-xs text-slate-300 transition-colors flex items-center gap-1.5"
                        >
                            <span>🔍</span> More Details
                        </button>
                    </div>
                )}

                {/* Input area */}
                <div className="border-t border-white/10 p-4 flex-shrink-0">
                    <div className="flex gap-2">
                        <input
                            ref={inputRef}
                            type="text"
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask a follow-up question..."
                            disabled={loading || isSending}
                            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-white text-sm outline-none focus:border-accent/50 transition-colors placeholder-slate-500 disabled:opacity-50"
                        />
                        <button
                            onClick={handleSend}
                            disabled={!userInput.trim() || loading || isSending}
                            className="px-4 py-2.5 bg-gradient-to-r from-accent to-emerald-500 text-slate-900 rounded-xl font-semibold text-sm hover:shadow-lg hover:shadow-accent/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            {isSending ? (
                                <>
                                    <div className="w-4 h-4 border-2 border-slate-900 border-t-transparent rounded-full animate-spin"></div>
                                    Sending
                                </>
                            ) : (
                                <>
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                    </svg>
                                    Send
                                </>
                            )}
                        </button>
                    </div>
                    <div className="flex items-center justify-between mt-2">
                        <div className="flex items-center gap-2 text-xs text-slate-500">
                            <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span>Powered by Google Gemini AI</span>
                        </div>
                        {news?.url && (
                            <a
                                href={news.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-accent hover:text-accent/80 font-medium transition-colors flex items-center gap-1"
                            >
                                Read Full Article
                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                            </a>
                        )}
                    </div>
                </div>
            </div>

            <style jsx>{`
                @keyframes fade-in {
                    from {
                        opacity: 0;
                    }
                    to {
                        opacity: 1;
                    }
                }

                @keyframes scale-in {
                    from {
                        opacity: 0;
                        transform: scale(0.95);
                    }
                    to {
                        opacity: 1;
                        transform: scale(1);
                    }
                }

                .animate-fade-in {
                    animation: fade-in 0.2s ease-out;
                }

                .animate-scale-in {
                    animation: scale-in 0.2s ease-out;
                }
            `}</style>
        </div>
    );
};

NewsSummaryModal.propTypes = {
    news: PropTypes.shape({
        title: PropTypes.string.isRequired,
        body: PropTypes.string.isRequired,
        url: PropTypes.string,
        sentiment: PropTypes.shape({
            label: PropTypes.string,
            score: PropTypes.number,
            confidence: PropTypes.number
        }),
    }),
    isOpen: PropTypes.bool.isRequired,
    onClose: PropTypes.func.isRequired,
};

export default NewsSummaryModal;
