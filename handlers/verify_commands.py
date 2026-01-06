"""验证命令处理器"""
import asyncio
import logging
import httpx
import time
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from config import VERIFY_COST
from database_mysql import Database
from one.sheerid_verifier import SheerIDVerifier as OneVerifier
from k12.sheerid_verifier import SheerIDVerifier as K12Verifier
from spotify.sheerid_verifier import SheerIDVerifier as SpotifyVerifier
from youtube.sheerid_verifier import SheerIDVerifier as YouTubeVerifier
from Boltnew.sheerid_verifier import SheerIDVerifier as BoltnewVerifier
from military.sheerid_verifier import SheerIDVerifier as MilitaryVerifier
from utils.messages import get_insufficient_balance_message, get_verify_usage_message

# 尝试导入并发控制，如果失败则使用空实现
try:
    from utils.concurrency import get_verification_semaphore
except ImportError:
    # 如果导入失败，创建一个简单的实现
    def get_verification_semaphore(verification_type: str):
        return asyncio.Semaphore(3)

logger = logging.getLogger(__name__)


async def verify_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /verify 命令 - Gemini One Pro"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You are blocked and cannot use this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please register with /start first.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify", "Gemini One Pro")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = OneVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Invalid SheerID link, please check and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Failed to deduct points, please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"Starting Gemini One Pro verification...\n"
        f"Verification ID: {verification_id}\n"
        f"Deducted {VERIFY_COST} points\n\n"
        "Please wait, this may take 1-2 minutes..."
    )

    try:
        verifier = OneVerifier(verification_id)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "gemini_one_pro",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Military verification successful!\n\n"
            if result.get("pending"):
                result_msg += "📋 Status: PENDING REVIEW\n"
                result_msg += "📄 DD-214 document uploaded successfully\n"
                result_msg += "⏱️ Estimated review time: 1-3 business days\n\n"
                result_msg += "💡 Tip: Check your email for updates from SheerID\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 Verification URL:\n{result['redirect_url']}"
            else:
                result_msg += result.get("message", "Verification completed!")
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            error_msg = result.get('message', 'Unknown error')
            tips = "\n\n💡 Tips:\n"
            if "email" in error_msg.lower():
                tips += "• Try using your own email: /verify6 [LINK] youremail@gmail.com\n"
            else:
                tips += "• Try with a fresh verification link\n"
                tips += "• Make sure the link is for Military/Veteran verification\n"
            
            await processing_msg.edit_text(
                f"❌ Verification failed: {error_msg}{tips}\n"
                f"💰 Refunded {VERIFY_COST} points"
            )
    except Exception as e:
        logger.error("Verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred during processing: {str(e)}\n\n"
            f"Refunded {VERIFY_COST} points"
        )


async def verify2_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /verify2 命令 - ChatGPT Teacher K12"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You are blocked and cannot use this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please register with /start first.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify2", "ChatGPT Teacher K12")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = K12Verifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Invalid SheerID link, please check and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Failed to deduct points, please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"Starting ChatGPT Teacher K12 verification...\n"
        f"Verification ID: {verification_id}\n"
        f"Deducted {VERIFY_COST} points\n\n"
        "Please wait, this may take 1-2 minutes..."
    )

    try:
        verifier = K12Verifier(verification_id)
        result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "chatgpt_teacher_k12",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Certification successful!\n\n"
            if result.get("pending"):
                result_msg += "Document submitted, waiting for manual review.\n"
            if result.get("redirect_url"):
                result_msg += f"Redirect URL:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Certification failed: {result.get('message', 'Unknown error')}\n\n"
                f"Refunded {VERIFY_COST} points"
            )
    except Exception as e:
        logger.error("Verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred during processing: {str(e)}\n\n"
            f"Refunded {VERIFY_COST} points"
        )


async def verify3_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /verify3 命令 - Spotify Student"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You are blocked and cannot use this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please register with /start first.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify3", "Spotify Student")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # 解析 verificationId
    verification_id = SpotifyVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Invalid SheerID link, please check and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Failed to deduct points, please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"🎵 Starting Spotify Student verification...\n"
        f"Deducted {VERIFY_COST} points\n\n"
        "📝 Generating student info...\n"
        "🎨 Generating student ID PNG...\n"
        "📤 Submitting document..."
    )

    # 使用信号量控制并发
    semaphore = get_verification_semaphore("spotify_student")

    try:
        async with semaphore:
            verifier = SpotifyVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "spotify_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ Spotify Student verification successful!\n\n"
            if result.get("pending"):
                result_msg += "✨ Document submitted, waiting for SheerID review\n"
                result_msg += "⏱️ Estimated review time: a few minutes\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 Redirect URL:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Certification failed: {result.get('message', 'Unknown error')}\n\n"
                f"Refunded {VERIFY_COST} points"
            )
    except Exception as e:
        logger.error("Spotify verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred during processing: {str(e)}\n\n"
            f"Refunded {VERIFY_COST} points"
        )



async def verify4_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /verify4 命令 - Bolt.new Teacher（自动获取code版）"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You are blocked and cannot use this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please register with /start first.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify4", "Bolt.new Teacher")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # 解析 externalUserId 或 verificationId
    external_user_id = BoltnewVerifier.parse_external_user_id(url)
    verification_id = BoltnewVerifier.parse_verification_id(url)

    if not external_user_id and not verification_id:
        await update.message.reply_text("Invalid SheerID link, please check and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Failed to deduct points, please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"🚀 Starting Bolt.new Teacher verification...\n"
        f"Deducted {VERIFY_COST} points\n\n"
        "📤 Submitting document..."
    )

    # 使用信号量控制并发
    semaphore = get_verification_semaphore("bolt_teacher")

    try:
        async with semaphore:
            # 第1步：提交文档
            verifier = BoltnewVerifier(url, verification_id=verification_id)
            result = await asyncio.to_thread(verifier.verify)

        if not result.get("success"):
            # 提交失败，退款
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Document submission failed: {result.get('message', 'Unknown error')}\n\n"
                f"Refunded {VERIFY_COST} points"
            )
            return
        
        vid = result.get("verification_id", "")
        if not vid:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Failed to get Verification ID\n\n"
                f"Refunded {VERIFY_COST} points"
            )
            return
        
        # 更新消息
        await processing_msg.edit_text(
            f"✅ Document submitted!\n"
            f"📋 Verification ID: `{vid}`\n\n"
            f"🔍 Auto-retrieving reward code...\n"
            f"(Max wait 20s)"
        )
        
        # 第2步：自动获取认证码（最多20秒）
        code = await _auto_get_reward_code(vid, max_wait=20, interval=5)
        
        if code:
            # 成功获取
            result_msg = (
                f"🎉 Verification successful!\n\n"
                f"✅ Document submitted\n"
                f"✅ Review passed\n"
                f"✅ Code retrieved\n\n"
                f"🎁 Reward Code: `{code}`\n"
            )
            if result.get("redirect_url"):
                result_msg += f"\n🔗 Redirect URL:\n{result['redirect_url']}"
            
            await processing_msg.edit_text(result_msg)
            
            # 保存成功记录
            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "success",
                f"Code: {code}",
                vid
            )
        else:
            # 20秒内未获取到，让用户稍后查询
            await processing_msg.edit_text(
                f"✅ Document submitted successfully!\n\n"
                f"⏳ Reward code not generated yet (Review may take 1-5 mins)\n\n"
                f"📋 Verification ID: `{vid}`\n\n"
                f"💡 Use this command to check later:\n"
                f"`/getV4Code {vid}`\n\n"
                f"Note: Points consumed, no extra charge for manual check."
            )
            
            # 保存待处理记录
            db.add_verification(
                user_id,
                "bolt_teacher",
                url,
                "pending",
                "Waiting for review",
                vid
            )
            
    except Exception as e:
        logger.error("Bolt.new verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred during processing: {str(e)}\n\n"
            f"Refunded {VERIFY_COST} points"
        )


async def _auto_get_reward_code(
    verification_id: str,
    max_wait: int = 20,
    interval: int = 5
) -> Optional[str]:
    """自动获取认证码（轻量级轮询，不影响并发）
    
    Args:
        verification_id: 验证ID
        max_wait: 最大等待时间（秒）
        interval: 轮询间隔（秒）
        
    Returns:
        str: 认证码，如果获取失败返回None
    """
    import time
    start_time = time.time()
    attempts = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            elapsed = int(time.time() - start_time)
            attempts += 1
            
            # 检查是否超时
            if elapsed >= max_wait:
                logger.info(f"自动获取code超时({elapsed}秒)，让用户手动查询")
                return None
            
            try:
                # 查询验证状态
                response = await client.get(
                    f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
                )
                
                if response.status_code == 200:
                    data = response.json()
                    current_step = data.get("currentStep")
                    
                    if current_step == "success":
                        # 获取认证码
                        code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
                        if code:
                            logger.info(f"✅ 自动获取code成功: {code} (耗时{elapsed}秒)")
                            return code
                    elif current_step == "error":
                        # 审核失败
                        logger.warning(f"审核失败: {data.get('errorIds', [])}")
                        return None
                    # else: pending，继续等待
                
                # 等待下次轮询
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.warning(f"查询认证码出错: {e}")
                await asyncio.sleep(interval)
    
    return None


async def verify5_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /verify5 命令 - YouTube Student Premium"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You are blocked and cannot use this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please register with /start first.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify5", "YouTube Student Premium")
        )
        return

    url = context.args[0]
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    # 解析 verificationId
    verification_id = YouTubeVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("Invalid SheerID link, please check and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("Failed to deduct points, please try again later.")
        return

    processing_msg = await update.message.reply_text(
        f"📺 Starting YouTube Student Premium verification...\n"
        f"Deducted {VERIFY_COST} points\n\n"
        "📝 Generating student info...\n"
        "🎨 Generating student ID PNG...\n"
        "📤 Submitting document..."
    )

    # 使用信号量控制并发
    semaphore = get_verification_semaphore("youtube_student")

    try:
        async with semaphore:
            verifier = YouTubeVerifier(verification_id)
            result = await asyncio.to_thread(verifier.verify)

        db.add_verification(
            user_id,
            "youtube_student",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            result_msg = "✅ YouTube Student Premium verification successful!\n\n"
            if result.get("pending"):
                result_msg += "✨ Document submitted, waiting for SheerID review\n"
                result_msg += "⏱️ Estimated review time: a few minutes\n\n"
            if result.get("redirect_url"):
                result_msg += f"🔗 Redirect URL:\n{result['redirect_url']}"
            await processing_msg.edit_text(result_msg)
        else:
            db.add_balance(user_id, VERIFY_COST)
            await processing_msg.edit_text(
                f"❌ Certification failed: {result.get('message', 'Unknown error')}\n\n"
                f"Refunded {VERIFY_COST} points"
            )
    except Exception as e:
        logger.error("YouTube verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        await processing_msg.edit_text(
            f"❌ An error occurred during processing: {str(e)}\n\n"
            f"Refunded {VERIFY_COST} points"
        )


async def getV4Code_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /getV4Code 命令 - 获取 Bolt.new Teacher 认证码"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("You are blocked and cannot use this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("Please register with /start first.")
        return

    # 检查是否提供了 verification_id
    if not context.args:
        await update.message.reply_text(
            "Usage: /getV4Code <verification_id>\n\n"
            "Example: /getV4Code 6929436b50d7dc18638890d0\n\n"
            "Verification ID is returned after using the /verify4 command."
        )
        return

    verification_id = context.args[0].strip()

    processing_msg = await update.message.reply_text(
        "🔍 Querying reward code, please wait..."
    )

    try:
        # 查询 SheerID API 获取认证码
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"https://my.sheerid.com/rest/v2/verification/{verification_id}"
            )

            if response.status_code != 200:
                await processing_msg.edit_text(
                    f"❌ Query failed, status code: {response.status_code}\n\n"
                    "Please try again later or contact admin."
                )
                return

            data = response.json()
            current_step = data.get("currentStep")
            reward_code = data.get("rewardCode") or data.get("rewardData", {}).get("rewardCode")
            redirect_url = data.get("redirectUrl")

            if current_step == "success" and reward_code:
                result_msg = "✅ Verification successful!\n\n"
                result_msg += f"🎉 Reward Code: `{reward_code}`\n\n"
                if redirect_url:
                    result_msg += f"Redirect URL:\n{redirect_url}"
                await processing_msg.edit_text(result_msg)
            elif current_step == "pending":
                await processing_msg.edit_text(
                    "⏳ Review still pending, please check back later.\n\n"
                    "Usually takes 1-5 mins, please be patient."
                )
            elif current_step == "error":
                error_ids = data.get("errorIds", [])
                await processing_msg.edit_text(
                    f"❌ Certification failed\n\n"
                    f"Error Details: {', '.join(error_ids) if error_ids else 'Unknown error'}"
                )
            else:
                await processing_msg.edit_text(
                    f"⚠️ Current Status: {current_step}\n\n"
                    "Reward code not generated yet, please try again later."
                )

    except Exception as e:
        logger.error("Failed to get Bolt.new code: %s", e)
        await processing_msg.edit_text(
            f"❌ An error occurred during query: {str(e)}\n\n"
            "Please try again later or contact admin."
        )


async def verify6_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """处理 /verify6 命令 - US Military/Veteran"""
    user_id = update.effective_user.id

    if db.is_user_blocked(user_id):
        await update.message.reply_text("🚫 You are blocked and cannot use this feature.")
        return

    if not db.user_exists(user_id):
        await update.message.reply_text("⚠️ Please register with /start first.")
        return

    if not context.args:
        await update.message.reply_text(
            get_verify_usage_message("/verify6", "US Military/Veteran")
        )
        return

    url = context.args[0]
    
    # Check if 'james' parameter is provided
    use_james_fixed = False
    custom_email = None
    
    for i in range(1, len(context.args)):
        arg = context.args[i].lower()
        if arg == 'james':
            use_james_fixed = True
        elif '@' in arg:  # Email parameter
            custom_email = arg
    
    user = db.get_user(user_id)
    if user["balance"] < VERIFY_COST:
        await update.message.reply_text(
            get_insufficient_balance_message(user["balance"])
        )
        return

    verification_id = MilitaryVerifier.parse_verification_id(url)
    if not verification_id:
        await update.message.reply_text("❌ Invalid SheerID link, please check and try again.")
        return

    if not db.deduct_balance(user_id, VERIFY_COST):
        await update.message.reply_text("❌ Failed to deduct points, please try again later.")
        return

    # ASCII Art Nero - Initial
    nero_frames = [
        """
```
    ⚔️ NERO MILITARY VERIFIER ⚔️
    
      ╔═══════════════════╗
      ║   INITIALIZING    ║
      ╚═══════════════════╝
           ⚙️ Loading...
```""",
        """
```
    ⚔️ NERO MILITARY VERIFIER ⚔️
    
      ╔═══════════════════╗
      ║   PROCESSING...   ║
      ║   [████░░░░░░░]   ║
      ╚═══════════════════╝
        🎯 Generating Identity
```""",
        """
```
    ⚔️ NERO MILITARY VERIFIER ⚔️
    
      ╔═══════════════════╗
      ║   PROCESSING...   ║
      ║   [████████░░░]   ║
      ╚═══════════════════╝
        📄 Creating DD-214
```""",
        """
```
    ⚔️ NERO MILITARY VERIFIER ⚔️
    
      ╔═══════════════════╗
      ║   PROCESSING...   ║
      ║   [███████████░]  ║
      ╚═══════════════════╝
        🚀 Submitting Data
```"""
    ]

    # Initial message with animation
    initial_msg = f"""
{nero_frames[0]}

╔══════════════════════════════════╗
║  🎖️ MILITARY VERIFICATION STARTED  ║
╚══════════════════════════════════╝

📧 Email: {"🔐 " + custom_email if custom_email else "🤖 Auto-Selected"}
🆔 ID: `{verification_id}`
💰 Cost: {VERIFY_COST} points

⏳ Estimated Time: 60-120 seconds
"""
    
    processing_msg = await update.message.reply_text(initial_msg, parse_mode='Markdown')

    # Animate frames
    try:
        for i, frame in enumerate(nero_frames[1:], 1):
            await asyncio.sleep(2)
            status_text = f"""
{frame}

╔══════════════════════════════════╗
║  📊 VERIFICATION IN PROGRESS [{i}/3] ║
╚══════════════════════════════════╝

📧 Email: {"🔐 " + custom_email if custom_email else "🤖 Auto-Selected"}
🆔 ID: `{verification_id}`

⏳ Please wait...
"""
            await processing_msg.edit_text(status_text, parse_mode='Markdown')
    except:
        pass  # Animation error non-critical

    try:
        verifier = MilitaryVerifier(verification_id)
        result = await asyncio.to_thread(verifier.verify, email=custom_email, use_james_fixed=use_james_fixed)

        db.add_verification(
            user_id,
            "military_veteran",
            url,
            "success" if result["success"] else "failed",
            str(result),
        )

        if result["success"]:
            # Success ASCII Art
            success_art = """
```
    ⚔️ NERO MILITARY VERIFIER ⚔️
    
      ╔═══════════════════╗
      ║   ✅ SUCCESS!     ║
      ║   [████████████]  ║
      ╚═══════════════════╝
           🎉 COMPLETED
```"""
            
            result_msg = success_art + "\n\n"
            result_msg += "╔══════════════════════════════════╗\n"
            result_msg += "║       🎖️ VERIFICATION RESULT        ║\n"
            result_msg += "╚══════════════════════════════════╝\n\n"
            
            if result.get("pending"):
                result_msg += "📋 **STATUS:** PENDING REVIEW\n\n"
                result_msg += "✅ DD-214 Document Uploaded\n"
                result_msg += "⏱️ Review Time: 1-3 Business Days\n"
                result_msg += "📧 Check Email for Updates\n\n"
                result_msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
            if result.get("redirect_url"):
                result_msg += f"🔗 **Verification Portal:**\n`{result['redirect_url']}`\n\n"
            else:
                result_msg += f"💬 {result.get('message', 'Verification completed!')}\n\n"
            
            result_msg += "═══════════════════════════\n"
            result_msg += "🎯 Powered by NERO Systems"
            
            await processing_msg.edit_text(result_msg, parse_mode='Markdown')
        else:
            # Failure ASCII Art
            fail_art = """
```
    ⚔️ NERO MILITARY VERIFIER ⚔️
    
      ╔═══════════════════╗
      ║   ❌ FAILED       ║
      ║   [████░░░░░░░]   ║
      ╚═══════════════════╝
         ⚠️ ERROR DETECTED
```"""
            
            db.add_balance(user_id, VERIFY_COST)
            error_msg = fail_art + "\n\n"
            error_msg += "╔══════════════════════════════════╗\n"
            error_msg += "║       ⚠️ VERIFICATION FAILED       ║\n"
            error_msg += "╚══════════════════════════════════╝\n\n"
            error_msg += f"❌ **Reason:**\n{result.get('message', 'Unknown error')}\n\n"
            
            if result.get("rate_limited"):
                error_msg += "⏰ **Solution:** Wait 10-15 minutes\n"
                error_msg += "🔗 Get a fresh verification link\n\n"
            
            error_msg += "━━━━━━━━━━━━━━━━━━━━━━\n"
            error_msg += f"💰 Refunded: {VERIFY_COST} points\n"
            error_msg += "═══════════════════════════\n"
            
            await processing_msg.edit_text(error_msg, parse_mode='Markdown')
            
    except Exception as e:
        logger.error("Military verification error: %s", e)
        db.add_balance(user_id, VERIFY_COST)
        
        # Exception ASCII Art
        exception_art = """
```
    ⚔️ NERO MILITARY VERIFIER ⚔️
    
      ╔═══════════════════╗
      ║   ⚠️ EXCEPTION    ║
      ║   [░░░░░░░░░░░░]  ║
      ╚═══════════════════╝
        🔧 SYSTEM ERROR
```"""
        
        error_msg = exception_art + "\n\n"
        error_msg += "╔══════════════════════════════════╗\n"
        error_msg += "║       🔧 SYSTEM ERROR              ║\n"
        error_msg += "╚══════════════════════════════════╝\n\n"
        error_msg += f"❌ **Error:**\n`{str(e)}`\n\n"
        error_msg += "━━━━━━━━━━━━━━━━━━━━━━\n"
        error_msg += f"💰 Refunded: {VERIFY_COST} points\n"
        error_msg += "📞 Contact: @admin\n"
        
        await processing_msg.edit_text(error_msg, parse_mode='Markdown')
        logger.info(
            f"Refunded {VERIFY_COST} points"
        )


async def test_ui_command(update: Update, context: ContextTypes.DEFAULT_TYPE, db: Database):
    """Test command to preview the animated NERO UI - Demo mode
    Usage: /testui [success/fail/exception]
    """
    user_id = update.effective_user.id

    # Check if user exists
    if not db.user_exists(user_id):
        await update.message.reply_text("Please register with /start first.")
        return

    # Get test scenario from args (default: success)
    scenario = "success"
    if context.args and len(context.args) > 0:
        scenario = context.args[0].lower()
    
    if scenario not in ["success", "fail", "exception"]:
        await update.message.reply_text(
            "**NERO Test UI**\n\n"
            "Usage: `/testui [scenario]`\n\n"
            "**Scenarios:**\n"
            "• `success` - Show successful verification\n"
            "• `fail` - Show failed verification\n"
            "• `exception` - Show exception screen\n\n"
            "Example: `/testui success`",
            parse_mode='Markdown'
        )
        return

    # Animation frames
    nero_frames = [
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║                               ║\n"
        "║     ███╗   ██╗███████╗██████╗  ║\n"
        "║     ████╗  ██║██╔════╝██╔══██╗ ║\n"
        "║     ██╔██╗ ██║█████╗  ██████╔╝ ║\n"
        "║     ██║╚██╗██║██╔══╝  ██╔══██╗ ║\n"
        "║     ██║ ╚████║███████╗██║  ██║ ║\n"
        "║     ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ║\n"
        "║                               ║\n"
        "║      MILITARY VERIFICATION    ║\n"
        "║           TEST MODE           ║\n"
        "║                               ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        "⏳ **INITIALIZING...**",
        
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║     ████ NERO SYSTEM ████     ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        "⚙️ **PROCESSING** [████░░░░░░░]\n"
        "📋 Generating Identity...",
        
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║     ████ NERO SYSTEM ████     ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        "⚙️ **PROCESSING** [████████░░░]\n"
        "🎖️ Creating DD-214 Document...",
        
        "```\n"
        "╔═══════════════════════════════╗\n"
        "║     ████ NERO SYSTEM ████     ║\n"
        "╚═══════════════════════════════╝\n"
        "```\n"
        "⚙️ **PROCESSING** [███████████]\n"
        "📤 Submitting to SheerID..."
    ]

    # Start animation
    processing_msg = await update.message.reply_text(nero_frames[0], parse_mode='Markdown')
    
    # Animate through frames
    for frame in nero_frames[1:]:
        await asyncio.sleep(2)
        await processing_msg.edit_text(frame, parse_mode='Markdown')

    # Final delay before showing result
    await asyncio.sleep(2)

    # Show result based on scenario
    if scenario == "success":
        success_art = (
            "```\n"
            "╔═══════════════════════════════════════╗\n"
            "║                                       ║\n"
            "║        ✅ VERIFICATION SUCCESS       ║\n"
            "║                                       ║\n"
            "║   ███╗   ██╗███████╗██████╗  ██████╗  ║\n"
            "║   ████╗  ██║██╔════╝██╔══██╗██╔═══██╗ ║\n"
            "║   ██╔██╗ ██║█████╗  ██████╔╝██║   ██║ ║\n"
            "║   ██║╚██╗██║██╔══╝  ██╔══██╗██║   ██║ ║\n"
            "║   ██║ ╚████║███████╗██║  ██║╚██████╔╝ ║\n"
            "║   ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ║\n"
            "║                                       ║\n"
            "╚═══════════════════════════════════════╝\n"
            "```\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚔️ **Veteran Profile:**\n"
            "`John D. Baca`\n\n"
            "🎖️ **Branch:**\n"
            "`U.S. Army - Medal of Honor Recipient`\n\n"
            "📧 **Email:**\n"
            "`johnbaca@carpkingdom.com`\n\n"
            "🆔 **Verification ID:**\n"
            "`test-demo-12345678-abcd`\n\n"
            "💾 **DD-214 Document:**\n"
            "`✓ Generated Successfully`\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💰 **Status:** No points deducted (TEST MODE)\n"
            "📞 **Support:** @admin\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        await processing_msg.edit_text(success_art, parse_mode='Markdown')
        
    elif scenario == "fail":
        fail_art = (
            "```\n"
            "╔═══════════════════════════════════════╗\n"
            "║                                       ║\n"
            "║         ❌ VERIFICATION FAILED         ║\n"
            "║                                       ║\n"
            "║   ███╗   ██╗███████╗██████╗  ██████╗  ║\n"
            "║   ████╗  ██║██╔════╝██╔══██╗██╔═══██╗ ║\n"
            "║   ██╔██╗ ██║█████╗  ██████╔╝██║   ██║ ║\n"
            "║   ██║╚██╗██║██╔══╝  ██╔══██╗██║   ██║ ║\n"
            "║   ██║ ╚████║███████╗██║  ██║╚██████╔╝ ║\n"
            "║   ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ║\n"
            "║                                       ║\n"
            "╚═══════════════════════════════════════╝\n"
            "```\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ **Error Type:**\n"
            "`notApproved`\n\n"
            "📝 **Details:**\n"
            "SheerID manual review required. This happens when:\n"
            "• Document quality needs human verification\n"
            "• Additional information required\n"
            "• System flagged for manual check\n\n"
            "🔄 **Next Steps:**\n"
            "1. Wait 24-48 hours for review\n"
            "2. Try with a different verification link\n"
            "3. Contact SheerID support directly\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💰 **Status:** No points deducted (TEST MODE)\n"
            "📞 **Support:** @admin\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        await processing_msg.edit_text(fail_art, parse_mode='Markdown')
        
    else:  # exception
        exception_art = (
            "```\n"
            "╔═══════════════════════════════════════╗\n"
            "║                                       ║\n"
            "║        ⚠️ SYSTEM EXCEPTION            ║\n"
            "║                                       ║\n"
            "║   ███╗   ██╗███████╗██████╗  ██████╗  ║\n"
            "║   ████╗  ██║██╔════╝██╔══██╗██╔═══██╗ ║\n"
            "║   ██╔██╗ ██║█████╗  ██████╔╝██║   ██║ ║\n"
            "║   ██║╚██╗██║██╔══╝  ██╔══██╗██║   ██║ ║\n"
            "║   ██║ ╚████║███████╗██║  ██║╚██████╔╝ ║\n"
            "║   ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ║\n"
            "║                                       ║\n"
            "╚═══════════════════════════════════════╝\n"
            "```\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "❌ **Error:**\n"
            "`Connection timeout - Network error`\n\n"
            "🔍 **Possible Causes:**\n"
            "• SheerID API temporarily unavailable\n"
            "• Network connectivity issues\n"
            "• Rate limiting protection activated\n\n"
            "🔄 **Recommended Actions:**\n"
            "1. Wait a few minutes and try again\n"
            "2. Check your internet connection\n"
            "3. Use a fresh verification link\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "💰 **Status:** No points deducted (TEST MODE)\n"
            "📞 **Support:** @admin\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        await processing_msg.edit_text(exception_art, parse_mode='Markdown')

    logger.info(f"User {user_id} tested UI with scenario: {scenario}")
