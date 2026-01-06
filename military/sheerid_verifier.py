"""SheerID Military Verification (Force Doc Upload Strategy)"""
import re
import random
import logging
import time
import httpx
from typing import Dict, Optional, Tuple

# Import lokal
try:
    from . import config
    from .data_utils import generate_military_identity
    from .img_generator import generate_dd214_image
except ImportError:
    import config
    from data_utils import generate_military_identity
    from img_generator import generate_dd214_image

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class SheerIDVerifier:
    def __init__(self, verification_id: str):
        self.verification_id = verification_id
        self.http_client = httpx.Client(timeout=45.0) # Timeout lebih lama untuk upload
        
        # MORE REALISTIC Browser Headers (reduce bot detection)
        chrome_version = random.choice(["120.0.0.0", "121.0.0.0", "122.0.0.0"])
        self.headers = {
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Origin": "https://services.sheerid.com",
            "Referer": f"https://services.sheerid.com/verify/{config.PROGRAM_ID}/",
            "Sec-Ch-Ua": f'"Not_A Brand";v="8", "Chromium";v="{chrome_version.split(".")[0]}", "Google Chrome";v="{chrome_version.split(".")[0]}"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }

    def __del__(self):
        self.http_client.close()

    @staticmethod
    def parse_verification_id(url: str) -> Optional[str]:
        match = re.search(r"verificationId=([a-f0-9]+)", url, re.IGNORECASE)
        if match: return match.group(1)
        return None

    def _request(self, method: str, endpoint: str, body: Optional[Dict] = None):
        """Helper request dengan error handling"""
        url = f"{config.SHEERID_BASE_URL}/rest/v2/verification/{self.verification_id}/{endpoint}"
        try:
            response = self.http_client.request(method, url, json=body, headers=self.headers)
            try:
                return response.json(), response.status_code
            except:
                return response.text, response.status_code
        except Exception as e:
            logger.error(f"Request Error: {e}")
            raise

    def _upload_s3(self, upload_url: str, data: bytes):
        """Upload file ke S3"""
        try:
            headers = {"Content-Type": "image/png"}
            resp = self.http_client.put(upload_url, content=data, headers=headers)
            return 200 <= resp.status_code < 300
        except Exception as e:
            logger.error(f"S3 Upload Error: {e}")
            return False

    def verify(self, email: Optional[str] = None, use_james_fixed: bool = False):
        """Main verification logic (Based on info.txt research)"""
        try:
            logger.info("⚔️ Memulai Misi Verifikasi Militer...")
            
            # 1. Generate Identitas Campuran
            if use_james_fixed:
                # Use fixed James Fleming identity (proven successful)
                identity = {
                    "first_name": "James",
                    "last_name": "Fleming",
                    "middle_initial": "P",
                    "full_name": "JAMES FLEMING",
                    "rank": "Captain",
                    "branch": "AIR_FORCE",
                    "dob": "1960-05-27",
                    "discharge_date": "1982-12-12",
                    "entry_date": "1978-12-12",
                    "ssn_last4": "5827"  # Fixed SSN last 4 digits
                }
                logger.info("🔒 Using FIXED James Fleming identity (proven successful)")
            else:
                identity = generate_military_identity()
            
            org_info = config.MILITARY_ORGS.get(identity['branch'], config.MILITARY_ORGS['ARMY'])
            
            logger.info(f"Target: {identity['full_name']} | Branch: {org_info['name']}")
            logger.info(f"DOB: {identity['dob']} | Discharge: {identity['discharge_date']}")

            # 2. Buat Dokumen DD-214
            logger.info("📄 Mencetak dokumen palsu DD-214...")
            img_data = generate_dd214_image(identity)
            logger.info(f"✅ Dokumen siap. Ukuran: {len(img_data)/1024:.2f} KB")

            time.sleep(random.uniform(3, 6))  # More natural human delay

            # 3. Langkah 1: Collect Military Status (Dropdown Selection)
            logger.info("Langkah 1: Set Status Veteran (Trigger collectMilitaryStatus)...")
            
            # FIXED: Menggunakan key 'status' bukan 'militaryStatus' sesuai error log
            step1_body = {
                "status": "VETERAN" 
            }
            
            data, status = self._request("POST", "step/collectMilitaryStatus", step1_body)
            
            if status != 200:
                # Fallback: Jika 'status' gagal, coba 'militaryStatus' lagi (untuk jaga-jaga program lama)
                logger.warning(f"Gagal pakai 'status', mencoba 'militaryStatus'...")
                step1_retry = {"militaryStatus": "VETERAN"}
                data, status = self._request("POST", "step/collectMilitaryStatus", step1_retry)
                
                if status != 200:
                    raise Exception(f"Gagal Step 1: {data}")

            # Ambil endpoint berikutnya dari respon (seharusnya collectInactiveMilitaryPersonalInfo)
            next_step = data.get("currentStep", "collectInactiveMilitaryPersonalInfo")
            logger.info(f"✅ Step 1 Sukses. Lanjut ke: {next_step}")

            time.sleep(random.uniform(4, 8))  # Longer delay before submitting personal info

            # 4. Langkah 2: Submit Personal Info (Include Discharge Date)
            logger.info(f"Langkah 2: Submit Data Diri ke {next_step}...")
            
            # PRIORITY EMAIL SELECTION:
            # 1. Custom email dari user (highest priority)
            # 2. Forwarding emails dari config (auto-forward ke email pribadi)
            # 3. Generated email (fallback)
            if email:
                final_email = email
                logger.info(f"📧 Using Custom Email: {final_email}")
            elif config.USE_FORWARDING_EMAILS and config.FORWARDING_EMAILS:
                # Gunakan forwarding email yang match dengan nama yang di-generate
                # Jika nama match, gunakan forwarding email yang sesuai
                forwarding_match = None
                for fwd_email in config.FORWARDING_EMAILS:
                    fwd_name = fwd_email.split('@')[0].lower()
                    if identity['first_name'].lower() in fwd_name or identity['last_name'].lower() in fwd_name:
                        forwarding_match = fwd_email
                        break
                
                if forwarding_match:
                    final_email = forwarding_match
                    logger.info(f"📧 Using Forwarding Email (Name Match): {final_email}")
                else:
                    # Jika tidak ada match, gunakan random forwarding email
                    final_email = random.choice(config.FORWARDING_EMAILS)
                    logger.info(f"📧 Using Forwarding Email (Random): {final_email}")
            else:
                # FALLBACK: Generate email dengan pattern natural
                domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
                birth_year = identity['dob'].split('-')[0][-2:]  # Last 2 digits of birth year
                
                # 70% chance: firstname.lastname[year]@domain
                # 30% chance: firstinitial.lastname[random]@domain (variasi)
                if random.random() < 0.7:
                    final_email = f"{identity['first_name'].lower()}.{identity['last_name'].lower()}{birth_year}@{random.choice(domains)}"
                else:
                    first_initial = identity['first_name'][0].lower()
                    final_email = f"{first_initial}.{identity['last_name'].lower()}{random.randint(100,999)}@{random.choice(domains)}"
                
                logger.info(f"📧 Generated Email: {final_email}")
            
            # Generate realistic device fingerprint (instead of repeating pattern)
            device_fingerprint = ''.join(random.choices('0123456789abcdef', k=64))
            
            step2_body = {
                "firstName": identity['first_name'],
                "lastName": identity['last_name'],
                "birthDate": identity['dob'],
                "dischargeDate": identity['discharge_date'], # DATA WAJIB UNTUK VETERAN
                "email": final_email,
                "phoneNumber": "",  # Empty but present (consistent with other verifiers)
                "organization": {
                    "id": org_info['id'],
                    "name": org_info['name']
                },
                "deviceFingerprintHash": device_fingerprint,  # Unique per request
                "locale": "en-US",
                "metadata": {
                    "marketConsentValue": False,
                    "refererUrl": f"{config.SHEERID_BASE_URL}/verify/{config.PROGRAM_ID}/?verificationId={self.verification_id}",
                    "verificationId": self.verification_id
                }
            }
            
            data, status = self._request("POST", f"step/{next_step}", step2_body)
            
            # Handle rate limiting
            if status == 429:
                error_data = data if isinstance(data, dict) else {}
                return {
                    "success": False,
                    "message": "⚠️ Rate Limit Exceeded!\n\nSheerID has blocked this verification link due to too many attempts.\n\nPlease:\n1. Wait 10-15 minutes\n2. Get a FRESH verification link from Discord/Website\n3. Try again with the new link\n\n💡 Tips:\n• Don't use the same link multiple times\n• Each verification needs a fresh link\n• SheerID tracks by IP and verification ID",
                    "rate_limited": True
                }
            
            if status != 200:
                raise Exception(f"Gagal Step 2 (HTTP {status}): {data}")
            
            current_step = data.get("currentStep")
            error_ids = data.get("errorIds", [])
            logger.info(f"✅ Step 2 Response: {current_step} | Errors: {error_ids if error_ids else 'None'}")

            # Handle Success
            if current_step == "success":
                return {"success": True, "message": "Instant Verification Successful!", "redirect_url": data.get("redirectUrl")}
            
            # Handle Email Loop - TRY TO SKIP FIRST (like SSO)
            if current_step == "emailLoop":
                logger.warning("⚠️ Masuk emailLoop - Mencoba skip dengan DELETE request...")
                time.sleep(random.uniform(2, 4))
                
                try:
                    skip_data, skip_status = self._request("DELETE", "step/emailLoop")
                    
                    if skip_status in [200, 204]:
                        # Berhasil skip emailLoop!
                        current_step = skip_data.get("currentStep", "docUpload") if isinstance(skip_data, dict) else "docUpload"
                        logger.info(f"✅ EmailLoop skipped successfully! Current: {current_step}")
                        time.sleep(random.uniform(2, 3))
                    else:
                        # Gagal skip emailLoop, TAPI coba force docUpload anyway
                        logger.warning(f"⚠️ Cannot skip emailLoop (HTTP {skip_status}), trying force docUpload...")
                        current_step = "docUpload"  # Force proceed
                        time.sleep(random.uniform(2, 3))
                except Exception as e:
                    # Error saat coba skip, force proceed ke docUpload anyway
                    logger.warning(f"⚠️ Exception while skipping emailLoop: {e}, trying force docUpload...")
                    current_step = "docUpload"
                    time.sleep(random.uniform(2, 3))

            # Handle Error State (notApproved, noMatch, etc) - FALLBACK TO DOCUPLOAD
            if current_step == "error":
                fallback_errors = ["notApproved", "noMatch", "notFound", "insufficientData"]
                can_upload = any(err in error_ids for err in fallback_errors)
                
                if can_upload:
                    logger.info(f"⚠️ Instant verification failed ({', '.join(error_ids)}), falling back to document upload...")
                    current_step = "docUpload"  # Force proceed to upload
                else:
                    raise Exception(f"Verification error: {', '.join(error_ids)}")
            
            # Skip SSO if present (like other verifiers)
            if current_step in ["sso", "collectInactiveMilitaryPersonalInfo"]:
                logger.info("Langkah 2.5: Skip SSO verification...")
                try:
                    data, status = self._request("DELETE", "step/sso")
                    if status == 200 or status == 204:
                        current_step = data.get("currentStep", current_step) if isinstance(data, dict) else current_step
                        logger.info(f"✅ SSO skipped. Current: {current_step}")
                    else:
                        logger.warning(f"SSO skip returned {status}, continuing...")
                    time.sleep(random.uniform(2, 3))
                except Exception as e:
                    logger.warning(f"Skip SSO failed (may not exist): {e}")
                    # Continue anyway, SSO might not be required

            # Validate we can proceed to upload
            if current_step not in ["docUpload", "error"]:
                return {
                    "success": False,
                    "message": f"Unexpected step: {current_step}. Cannot upload document.",
                    "verification_id": self.verification_id
                }

            # 5. Langkah 3: Upload Document
            logger.info("Langkah 3: Request document upload slot...")
            time.sleep(random.uniform(3, 5))
            
            step3_body = {
                "files": [
                    {"fileName": "DD214_Discharge.png", "mimeType": "image/png", "fileSize": len(img_data)}
                ]
            }
            
            data, status = self._request("POST", "step/docUpload", step3_body)
            
            # Handle jika docUpload gagal karena masih di emailLoop state
            if status != 200:
                error_detail = data if isinstance(data, dict) else {}
                error_msg = error_detail.get('systemErrorMessage', str(data))
                
                # Cek apakah gagal karena emailLoop yang belum resolved
                if 'email' in error_msg.lower() or 'emailLoop' in str(error_detail):
                    logger.error(f"❌ DocUpload blocked by emailLoop requirement")
                    return {
                        "success": False,
                        "message": f"📧 Email verification required!\n\nSheerID sent verification to:\n{final_email}\n\n✅ Email will forward to your personal inbox (Surfshark)\n\nPlease:\n1. Check your personal email inbox/spam\n2. Find email from SheerID\n3. Click verification link\n4. After verified, use fresh verification link\n\n💡 Tip: Email forwarding is active, you should receive it soon!",
                        "email": final_email,
                        "verification_id": self.verification_id
                    }
                else:
                    raise Exception(f"Failed to request upload slot (HTTP {status}): {error_detail}")
            
            if not data.get("documents") or len(data['documents']) == 0:
                raise Exception("Upload slot not received from SheerID")
                
            upload_url = data['documents'][0]['uploadUrl']
            logger.info("✅ Upload slot received")
            
            if self._upload_s3(upload_url, img_data):
                logger.info("✅ S3 Upload Successful!")
            else:
                raise Exception("S3 Upload Failed")

            # 6. Finalize
            logger.info("Langkah 4: Finalize document submission...")
            time.sleep(random.uniform(1, 2))
            
            data, status = self._request("POST", "step/completeDocUpload")
            logger.info(f"✅ Document submitted: {data.get('currentStep')}")
            
            return {
                "success": True,
                "pending": True,
                "message": "✅ Military document submitted successfully! Waiting for manual review (usually 1-3 business days).",
                "verification_id": self.verification_id,
                "redirect_url": data.get("redirectUrl")
            }

        except Exception as e:
            logger.error(f"Verifikasi Gagal: {e}")
            return {"success": False, "message": str(e)}

if __name__ == "__main__":
    # Test Mode
    url = input("Masukkan Link Military: ")
    vid = SheerIDVerifier.parse_verification_id(url)
    if vid:
        verifier = SheerIDVerifier(vid)
        print(verifier.verify())
    else:
        print("Invalid URL")
