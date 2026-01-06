import json
import random
import os
from datetime import datetime, timedelta

def load_military_names():
    """Load names from militarydata.json"""
    try:
        # Mencoba path relatif
        path = os.path.join(os.path.dirname(__file__), 'militarydata.json')
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        candidates = []
        # Ambil dari daftar penerima Medal of Honor yang kurang dikenal (lebih aman)
        if 'lesser_known_living_medal_of_honor_recipients' in data:
            candidates.extend(data['lesser_known_living_medal_of_honor_recipients'])
        
        # Fallback ke daftar umum jika kosong
        if not candidates and 'living_medal_of_honor_recipients' in data:
            candidates.extend(data['living_medal_of_honor_recipients'])
            
        return candidates
    except Exception as e:
        print(f"Error loading military data: {e}")
        return []

def generate_military_identity():
    """Generate a complete fake military profile based on real names"""
    candidates = load_military_names()
    
    if not candidates:
        # Fallback identity if JSON fails
        return {
            "first_name": "John",
            "last_name": "Doe",
            "rank": "Sergeant",
            "branch": "ARMY",
            "dob": "1985-05-15",
            "discharge_date": "2015-05-15",
            "entry_date": "2011-05-15"
        }

    # Pilih veteran secara RANDOM
    person = random.choice(candidates)
    full_name = person['name'].split()
    first_name = full_name[0]
    
    # Handle suffix (Jr., Sr., III, etc)
    suffixes = ['Jr.', 'Sr.', 'II', 'III', 'IV']
    if full_name[-1] in suffixes and len(full_name) > 2:
        # Ada suffix, ambil kata kedua terakhir sebagai last name
        last_name = full_name[-2]
    else:
        # Tidak ada suffix, ambil kata terakhir
        last_name = full_name[-1]

    # Generate Tanggal Lahir (Usia 30-50 tahun untuk Veteran)
    # Veteran Vietnam (di JSON) biasanya lahir 1940-1955
    # Tapi kita buat agak acak agar 'Gagal' di database check (itu tujuannya!)
    year = random.randint(1950, 1985) 
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    dob = f"{year}-{month:02d}-{day:02d}"

    # Generate Tanggal Dinas (3-4 tahun dinas)
    entry_year = year + 18 # Masuk umur 18
    entry_month = random.randint(1, 12)
    entry_day = random.randint(1, 28)
    entry_date = f"{entry_year}-{entry_month:02d}-{entry_day:02d}"

    discharge_year = entry_year + random.randint(3, 6)
    discharge_date = f"{discharge_year}-{entry_month:02d}-{entry_day:02d}"

    # Mapping Branch Name ke Kode SheerID
    raw_branch = person.get('branch', 'US Army').upper()
    if 'NAVY' in raw_branch: branch_code = 'NAVY'
    elif 'AIR FORCE' in raw_branch: branch_code = 'AIR_FORCE'
    elif 'MARINE' in raw_branch: branch_code = 'MARINE_CORPS'
    elif 'COAST' in raw_branch: branch_code = 'COAST_GUARD'
    else: branch_code = 'ARMY'

    # Generate middle initial (random A-Z)
    middle_initial = random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ')  # Skip I and O
    
    return {
        "first_name": first_name,
        "last_name": last_name,
        "middle_initial": middle_initial,
        "full_name": f"{first_name} {last_name}".upper(),
        "rank": person.get('rank', 'Specialist'),
        "branch": branch_code,
        "dob": dob,
        "entry_date": entry_date,
        "discharge_date": discharge_date,
        "ssn_last4": str(random.randint(1000, 9999)) # Fake SSN
    }
