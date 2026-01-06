"""Generator Dokumen DD-214 (Military Discharge)"""
import random
from datetime import datetime
from io import BytesIO

def generate_dd214_html(identity):
    """
    Membuat HTML DD-214 dengan gaya mesin ketik jadul
    """
    
    # Efek Scan: Rotasi sedikit dan background noise
    rotation = random.uniform(-0.4, 0.4)
    
    # Dynamic data based on branch
    branch_code = identity['branch']
    branch_display = {
        'ARMY': 'ARMY',
        'NAVY': 'NAVY',
        'AIR_FORCE': 'AIR FORCE',
        'MARINE_CORPS': 'USMC',
        'COAST_GUARD': 'USCG',
        'SPACE_FORCE': 'SPACE FORCE'
    }.get(branch_code, 'ARMY')
    
    # Dynamic duty assignment by branch
    duty_assignments = {
        'ARMY': 'HHC 1ST BATTALION, 5TH INFANTRY',
        'NAVY': 'USS NIMITZ CVN-68, CARRIER GROUP',
        'AIR_FORCE': '1ST FIGHTER WING, LANGLEY AFB',
        'MARINE_CORPS': '2ND MARINE DIVISION, CAMP LEJEUNE',
        'COAST_GUARD': 'USCG SECTOR SAN DIEGO',
        'SPACE_FORCE': 'SPACE OPERATIONS COMMAND'
    }
    duty_station = duty_assignments.get(branch_code, duty_assignments['ARMY'])
    
    # Dynamic separation stations by branch
    separation_stations = {
        'ARMY': 'FORT HOOD, TX',
        'NAVY': 'NORFOLK, VA',
        'AIR_FORCE': 'LANGLEY AFB, VA',
        'MARINE_CORPS': 'CAMP LEJEUNE, NC',
        'COAST_GUARD': 'SAN DIEGO, CA',
        'SPACE_FORCE': 'PETERSON SFB, CO'
    }
    sep_station = separation_stations.get(branch_code, separation_stations['ARMY'])
    
    # Dynamic medals by branch
    medals_by_branch = {
        'ARMY': 'NATIONAL DEFENSE SERVICE MEDAL // GWOT SERVICE MEDAL // ARMY SERVICE RIBBON // MARKSMANSHIP BADGE',
        'NAVY': 'NATIONAL DEFENSE SERVICE MEDAL // GWOT SERVICE MEDAL // NAVY GOOD CONDUCT MEDAL // SEA SERVICE RIBBON',
        'AIR_FORCE': 'NATIONAL DEFENSE SERVICE MEDAL // GWOT SERVICE MEDAL // AF GOOD CONDUCT MEDAL // AF TRAINING RIBBON',
        'MARINE_CORPS': 'NATIONAL DEFENSE SERVICE MEDAL // GWOT SERVICE MEDAL // MARINE CORPS GOOD CONDUCT MEDAL',
        'COAST_GUARD': 'NATIONAL DEFENSE SERVICE MEDAL // GWOT SERVICE MEDAL // CG GOOD CONDUCT MEDAL',
        'SPACE_FORCE': 'NATIONAL DEFENSE SERVICE MEDAL // GWOT SERVICE MEDAL // SF TRAINING RIBBON'
    }
    medals = medals_by_branch.get(branch_code, medals_by_branch['ARMY'])
    
    # Dynamic separation authority by branch
    separation_authorities = {
        'ARMY': 'AR 635-200, CHAP 4',
        'NAVY': 'MILPERSMAN 1910-308',
        'AIR_FORCE': 'AFI 36-3208',
        'MARINE_CORPS': 'MCO 1900.16',
        'COAST_GUARD': 'COMDTINST M1000.4',
        'SPACE_FORCE': 'SPFI 36-3208'
    }
    sep_authority = separation_authorities.get(branch_code, separation_authorities['ARMY'])
    
    # Middle initial
    middle_initial = identity.get('middle_initial', 'J')
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Courier+Prime&family=Special+Elite&display=swap');

        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 40px;
            background-color: #fcfcfc; /* Kertas agak tua */
            color: #111;
            transform: rotate({rotation}deg);
        }}

        .form-container {{
            border: 2px solid #000;
            padding: 5px;
            width: 1000px;
            height: 1200px;
            position: relative;
            background-image: url('https://www.transparenttextures.com/patterns/dust.png'); /* Efek debu/scan */
        }}

        .header {{
            text-align: center;
            border-bottom: 2px solid #000;
            padding-bottom: 5px;
            margin-bottom: 0;
        }}
        
        .header h2 {{ margin: 5px 0; font-size: 18px; text-transform: uppercase; }}
        .header h3 {{ margin: 2px 0; font-size: 14px; font-weight: normal; }}

        /* Kotak-kotak form */
        .row {{
            display: flex;
            border-bottom: 1px solid #000;
        }}
        
        .cell {{
            border-right: 1px solid #000;
            padding: 4px 8px;
            font-size: 10px;
            position: relative;
        }}
        
        .cell:last-child {{ border-right: none; }}
        
        .label {{
            display: block;
            font-weight: bold;
            text-transform: uppercase;
            font-size: 9px;
            margin-bottom: 2px;
        }}
        
        /* Font Mesin Ketik untuk isian */
        .value {{
            font-family: 'Courier Prime', 'Courier New', monospace;
            font-size: 14px;
            font-weight: bold;
            color: #222; /* Tinta hitam agak pudar */
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .footer {{
            position: absolute;
            bottom: 10px;
            left: 0;
            width: 100%;
            text-align: center;
            font-size: 10px;
            border-top: 2px solid #000;
            padding-top: 5px;
        }}

    </style>
</head>
<body>

<div class="form-container">
    <div class="header">
        <h2>Certificate of Release or Discharge from Active Duty</h2>
        <h3>DD FORM 214</h3>
    </div>

    <!-- Row 1: Name, Dept, SSN -->
    <div class="row">
        <div class="cell" style="width: 40%;">
            <span class="label">1. Name (Last, First, Middle)</span>
            <span class="value">{identity['last_name']}, {identity['first_name']} {middle_initial}.</span>
        </div>
        <div class="cell" style="width: 20%;">
            <span class="label">2. Department</span>
            <span class="value">{branch_display}</span>
        </div>
        <div class="cell" style="width: 20%;">
            <span class="label">3. Social Security No.</span>
            <span class="value">***-**-{identity['ssn_last4']}</span>
        </div>
        <div class="cell" style="width: 20%;">
            <span class="label">4. Grade, Rate or Rank</span>
            <span class="value">{identity['rank'].upper()}</span>
        </div>
    </div>

    <!-- Row 2: DOB, Reserve Oblig -->
    <div class="row">
        <div class="cell" style="width: 30%;">
            <span class="label">5. Date of Birth</span>
            <span class="value">{identity['dob']}</span>
        </div>
        <div class="cell" style="width: 30%;">
            <span class="label">6. Reserve Oblig. Term. Date</span>
            <span class="value">N/A</span>
        </div>
        <div class="cell" style="width: 40%;">
            <span class="label">7. Place of Entry into Active Duty</span>
            <span class="value">MEPS LOS ANGELES, CA</span>
        </div>
    </div>

    <!-- Row 3: Last Duty Station -->
    <div class="row">
        <div class="cell" style="width: 50%;">
            <span class="label">8. Last Duty Assignment and Major Command</span>
            <span class="value">{duty_station}</span>
        </div>
        <div class="cell" style="width: 50%;">
            <span class="label">9. Station Where Separated</span>
            <span class="value">{sep_station}</span>
        </div>
    </div>

    <!-- Row 4: Service Dates -->
    <div class="row">
        <div class="cell" style="width: 100%;">
            <span class="label">12. Record of Service</span>
            <table style="width: 100%; border-collapse: collapse; font-family: 'Courier Prime', monospace; font-size: 12px;">
                <tr>
                    <td style="width: 50%;"></td>
                    <td>Year</td>
                    <td>Month</td>
                    <td>Day</td>
                </tr>
                <tr>
                    <td>a. Date Entered AD This Period</td>
                    <td>{identity['entry_date'].split('-')[0]}</td>
                    <td>{identity['entry_date'].split('-')[1]}</td>
                    <td>{identity['entry_date'].split('-')[2]}</td>
                </tr>
                <tr>
                    <td>b. Separation Date This Period</td>
                    <td>{identity['discharge_date'].split('-')[0]}</td>
                    <td>{identity['discharge_date'].split('-')[1]}</td>
                    <td>{identity['discharge_date'].split('-')[2]}</td>
                </tr>
            </table>
        </div>
    </div>

    <!-- Row 5: Decorations -->
    <div class="row" style="height: 100px;">
        <div class="cell" style="width: 100%;">
            <span class="label">13. Decorations, Medals, Badges, Citations and Campaign Ribbons</span>
            <div class="value" style="margin-top: 5px;">
                {medals}
            </div>
        </div>
    </div>

    <!-- Row 6: Education -->
    <div class="row" style="height: 80px;">
        <div class="cell" style="width: 100%;">
            <span class="label">14. Military Education</span>
            <div class="value" style="margin-top: 5px;">
                BASIC COMBAT TRAINING, 10 WEEKS // ADVANCED INDIVIDUAL TRAINING, 8 WEEKS
            </div>
        </div>
    </div>

    <!-- Bottom Section: Discharge Info (CRITICAL FOR SHEERID) -->
    <div style="position: absolute; bottom: 150px; width: 100%; border-top: 2px solid #000;">
        <div class="row">
            <div class="cell" style="width: 30%;">
                <span class="label">23. Type of Separation</span>
                <span class="value">DISCHARGE</span>
            </div>
            <div class="cell" style="width: 30%;">
                <span class="label">24. Character of Service</span>
                <span class="value">HONORABLE</span>
            </div>
            <div class="cell" style="width: 40%;">
                <span class="label">25. Separation Authority</span>
                <span class="value">{sep_authority}</span>
            </div>
        </div>
        <div class="row">
            <div class="cell" style="width: 30%;">
                <span class="label">26. Separation Code</span>
                <span class="value">JBK</span>
            </div>
            <div class="cell" style="width: 30%;">
                <span class="label">27. Reentry Code</span>
                <span class="value">RE-1</span>
            </div>
            <div class="cell" style="width: 40%;">
                <span class="label">28. Narrative Reason for Separation</span>
                <span class="value">COMPLETION OF REQUIRED ACTIVE SERVICE</span>
            </div>
        </div>
    </div>

    <div class="footer">
        DD FORM 214, AUG 2009 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; PREVIOUS EDITIONS ARE OBSOLETE.
    </div>
</div>

</body>
</html>
"""
    return html

def generate_dd214_image(identity):
    """
    Render HTML to PNG using Playwright
    """
    try:
        from playwright.sync_api import sync_playwright
        
        html_content = generate_dd214_html(identity)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1100, 'height': 1300})
            page.set_content(html_content, wait_until='load')
            # Screenshot elemen form-container saja agar pas
            element = page.locator('.form-container')
            screenshot_bytes = element.screenshot(type='png')
            browser.close()
            
        return screenshot_bytes
    except Exception as e:
        raise Exception(f"Failed to generate DD-214: {str(e)}")
