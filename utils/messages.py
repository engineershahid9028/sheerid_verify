"""Message Templates"""
from config import CHANNEL_URL, VERIFY_COST, HELP_NOTION_URL


def get_welcome_message(full_name: str, invited_by: bool = False) -> str:
    """Get welcome message"""
    msg = (
        f"🎉 Welcome, {full_name}!\n"
        "You have successfully registered and received 1 point.\n"
    )
    if invited_by:
        msg += "Thanks for joining via invitation! Your inviter received 2 points.\n"

    msg += (
        "\nThis bot automates SheerID verification.\n"
        "Quick Start:\n"
        "/about - Bot features\n"
        "/balance - Check points\n"
        "/help - Full command list\n\n"
        "Get more points:\n"
        "/qd - Daily check-in\n"
        "/invite - Invite friends\n"
        f"Join Channel: {CHANNEL_URL}"
    )
    return msg


def get_about_message() -> str:
    """Get about message"""
    return (
        "🤖 SheerID Auto-Verification Bot\n"
        "\n"
        "Features:\n"
        "- Automates SheerID Student/Teacher verification\n"
        "- Supports Gemini One Pro, ChatGPT Teacher K12, Spotify Student, YouTube Student, Bolt.new Teacher\n"
        "\n"
        "Points System:\n"
        "- Registration: +1 point\n"
        "- Daily Check-in: +1 point\n"
        "- Invite Friends: +2 points/person\n"
        "- Redeem Codes (Based on code value)\n"
        f"- Join Channel: {CHANNEL_URL}\n"
        "\n"
        "How to use:\n"
        "1. Start verification on the website and copy the FULL verification link.\n"
        "2. Send /verify, /verify2, /verify3, /verify4 or /verify5 with the link.\n"
        "3. Wait for processing and results.\n"
        "4. Bolt.new verification auto-retrieves the code. Use /getV4Code <id> to check manually.\n"
        "\n"
        "Send /help for more commands."
    )


def get_help_message(is_admin: bool = False) -> str:
    """Get help message"""
    msg = (
        "📖 SheerID Bot - Help\n"
        "\n"
        "User Commands:\n"
        "/start - Start/Register\n"
        "/about - About Bot\n"
        "/balance - Check Balance\n"
        "/qd - Daily Check-in (+1 point)\n"
        "/invite - Invite Link (+2 points/person)\n"
        "/use <code> - Redeem Code\n"
        f"/verify <link> - Gemini One Pro (-{VERIFY_COST} pts)\n"
        f"/verify2 <link> - ChatGPT Teacher K12 (-{VERIFY_COST} pts)\n"
        f"/verify3 <link> - Spotify Student (-{VERIFY_COST} pts)\n"
        f"/verify4 <link> - Bolt.new Teacher (-{VERIFY_COST} pts)\n"
        f"/verify5 <link> - YouTube Student Premium (-{VERIFY_COST} pts)\n"
        f"/verify6 <link> - US Military/Veteran (-{VERIFY_COST} pts)\n"
        "/getV4Code <id> - Get Bolt.new Code\n"
        "/help - Show this help\n"
        f"Verification Issues: {HELP_NOTION_URL}\n"
    )

    if is_admin:
        msg += (
            "\nAdmin Commands:\n"
            "/addbalance <UserID> <Points> - Add points\n"
            "/block <UserID> - Block user\n"
            "/white <UserID> - Unblock user\n"
            "/blacklist - View blacklist\n"
            "/genkey <Code> <Points> [Uses] [Days] - Generate key\n"
            "/listkeys - List keys\n"
            "/broadcast <Text> - Broadcast message\n"
        )

    return msg


def get_insufficient_balance_message(current_balance: int) -> str:
    """Get insufficient balance message"""
    return (
        f"Insufficient points! Need {VERIFY_COST} points, you have {current_balance}.\n\n"
        "How to get points:\n"
        "- Daily Check-in /qd\n"
        "- Invite Friends /invite\n"
        "- Redeem Code /use <code>"
    )


def get_verify_usage_message(command: str, service_name: str) -> str:
    """Get verify usage message"""
    return (
        f"Usage: {command} <SheerID Link>\n\n"
        "Example:\n"
        f"{command} https://services.sheerid.com/verify/xxx/?verificationId=xxx\n\n"
        "How to get link:\n"
        f"1. Visit {service_name} verification page.\n"
        "2. Start the process.\n"
        "3. Copy the FULL URL from the browser address bar.\n"
        f"4. Send using {command} command."
    )
