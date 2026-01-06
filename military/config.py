# SheerID Military Verification Config

# Program ID untuk Military (Contoh umum, harus diupdate jika beda)
PROGRAM_ID = '690415d58971e73ca187d8c9' 

SHEERID_BASE_URL = 'https://services.sheerid.com'
MY_SHEERID_URL = 'https://my.sheerid.com'

# Pemetaan ID Cabang (Berdasarkan info.txt)
MILITARY_ORGS = {
    'ARMY': {'id': 4070, 'name': 'Army'},
    'AIR_FORCE': {'id': 4073, 'name': 'Air Force'},
    'NAVY': {'id': 4072, 'name': 'Navy'},
    'MARINE_CORPS': {'id': 4071, 'name': 'Marine Corps'},
    'COAST_GUARD': {'id': 4074, 'name': 'Coast Guard'},
    'SPACE_FORCE': {'id': 4544268, 'name': 'Space Force'}
}

# Organisasi Reservist (ID Berbeda)
RESERVIST_ORGS = {
    'ARMY_NATIONAL_GUARD': {'id': 4075, 'name': 'Army National Guard'},
    'ARMY_RESERVE': {'id': 4076, 'name': 'Army Reserve'},
    'AIR_NATIONAL_GUARD': {'id': 4079, 'name': 'Air National Guard'},
    'AIR_FORCE_RESERVE': {'id': 4080, 'name': 'Air Force Reserve'},
    'NAVY_RESERVE': {'id': 4078, 'name': 'Navy Reserve'},
    'MARINE_RESERVE': {'id': 4077, 'name': 'Marine Corps Forces Reserve'},
    'COAST_GUARD_RESERVE': {'id': 4081, 'name': 'Coast Guard Reserve'}
}

# Email Forwarding (Surfshark/Custom Domain)
# Email-email ini akan auto-forward ke email pribadi Anda
# SheerID akan kirim verification ke email ini → Auto forward → Anda terima
FORWARDING_EMAILS = [
    "johnbaca@carpkingdom.com",  # John Baca (Surfshark forward)
    # Tambahkan lebih banyak forwarding emails di sini jika punya
    # "donaldballard@carpkingdom.com",
    # "dwightbirdwell@carpkingdom.com",
]

# Feature Flag: Gunakan forwarding email by default?
USE_FORWARDING_EMAILS = True  # Set False untuk disable auto-use forwarding emails
