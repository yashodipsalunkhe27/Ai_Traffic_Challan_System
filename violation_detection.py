import os
import base64
import sqlite3
import re
from groq import RateLimitError

from dotenv import load_dotenv

load_dotenv()

import streamlit as st
from groq import Groq


# =========================================================
# GROQ API
# =========================================================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set."
    )

client = Groq(
    api_key=GROQ_API_KEY
)


# =========================================================
# NORMALIZE NUMBER PLATE
# =========================================================

def normalize_plate(plate):

    if not plate:
        return ""

    return "".join(
        ch
        for ch in str(plate).upper()
        if ch.isalnum()
    )


# =========================================================
# DETECT TRAFFIC VIOLATION
# =========================================================

def detect_violation(image_path):

    with open(image_path, "rb") as f:

        image_base64 = base64.b64encode(
            f.read()
        ).decode("utf-8")


    response = client.chat.completions.create(

        model="qwen/qwen3.8-27b",

        max_tokens=300,

        temperature=0,

        reasoning_effort="none",

        messages=[

            {
                "role": "user",

                "content": [

                    {
                        "type": "text",

                        "text": """
Analyze this traffic image.

Identify ONLY ONE violation.

Allowed violations:

1. Triple Ride
2. No Parking
3. No Helmet
4. Overspeed

Return ONLY one of these exact names:

Triple Ride
No Parking
No Helmet
Overspeed

Do not provide:
- reasoning
- explanation
- markdown
- <think> tags
- additional text
"""
                    },

                    {
                        "type": "image_url",

                        "image_url": {

                            "url":
                            f"data:image/jpeg;base64,{image_base64}"

                        }
                    }

                ]
            }
        ]
    )


    result = response.choices[0].message.content.strip()


    # =====================================================
    # REMOVE THINK TAGS
    # =====================================================

    if "<think>" in result:

        if "</think>" in result:

            result = result.split(
                "</think>"
            )[-1]

        else:

            result = result.split(
                "<think>"
            )[-1]


    result = result.strip()

    result_lower = result.lower()


    # =====================================================
    # IDENTIFY VIOLATION
    # =====================================================

    if "triple ride" in result_lower:

        return "Triple Ride"


    if "no parking" in result_lower:

        return "No Parking"


    if "no helmet" in result_lower:

        return "No Helmet"


    if "overspeed" in result_lower:

        return "Overspeed"


    # =====================================================
    # HANDLE SLIGHT MODEL VARIATIONS
    # =====================================================

    if "triple" in result_lower:

        return "Triple Ride"


    if "parking" in result_lower:

        return "No Parking"


    if "helmet" in result_lower:

        return "No Helmet"


    if "overspeed" in result_lower:

        return "Overspeed"


    return result


# =========================================================
# DETECT NUMBER PLATE
# =========================================================

def detect_number_plate(image_path):

    with open(image_path, "rb") as f:

        image_base64 = base64.b64encode(
            f.read()
        ).decode("utf-8")


    response = client.chat.completions.create(

        model="qwen/qwen3.8-27b",

        max_tokens=400,

        temperature=0,

        reasoning_effort="none",

        messages=[

            {
                "role": "user",

                "content": [

                    {
                        "type": "text",

                        "text": """
You are an Indian vehicle number plate reader.

Look carefully at the image.

Find the clearest, most legible Indian vehicle
registration plate visible anywhere in the image —
it may belong to a car, bike, scooter, bus, or any
other vehicle.

If NO vehicle number plate is clearly legible anywhere
in the image, return exactly:

NOTFOUND

Do NOT guess, invent, or reconstruct a plate number if
none is clearly readable.

If a plate IS clearly visible, read the COMPLETE
registration number from that plate.

Return ONLY the complete registration number, or NOTFOUND.

Example:

TS09PA3330

Rules:

- Return exactly ONE vehicle registration number, or NOTFOUND.
- Include ALL letters and ALL digits.
- Do NOT return only the state code.
- Do NOT return only TS09PA.
- Do NOT explain anything.
- Do NOT describe the image.
- Do NOT provide reasoning.
- Do NOT provide instructions.
- Do NOT use <think>.
- Do NOT use markdown.
- Do NOT write "Number Plate".
- Do NOT write "Registration".
- Return only letters and numbers.

Your final answer must look like:

TS09PA3330
"""
                    },

                    {
                        "type": "image_url",

                        "image_url": {

                            "url":
                            f"data:image/jpeg;base64,{image_base64}"

                        }
                    }

                ]
            }
        ]
    )


    result = response.choices[0].message.content.strip()


    # =====================================================
    # REMOVE THINKING TEXT
    # =====================================================

    if "<think>" in result:

        if "</think>" in result:

            result = result.split(
                "</think>"
            )[-1]

        else:

            result = result.split(
                "<think>"
            )[-1]


    result = result.upper().strip()


    if "NOTFOUND" in result:
        return "NOTFOUND"


    # =====================================================
    # SEARCH COMPLETE INDIAN NUMBER PLATE


    # =====================================================
    # SEARCH COMPLETE INDIAN NUMBER PLATE
    #
    # Examples:
    #
    # TS09PA3330
    # MH12AB1234
    # KA01AA1234
    # =====================================================

    matches = re.findall(
        r"[A-Z]{2}\s*\d{1,2}\s*[A-Z]{1,3}\s*\d{3,4}",
        result
    )


    if matches:

        plate = matches[0]

        plate = re.sub(
            r"[^A-Z0-9]",
            "",
            plate
        )

        return plate


    # =====================================================
    # SECOND PATTERN
    #
    # Handles text like:
    #
    # THEWHITESUV...ITREADSTS09PA3330
    # =====================================================

    matches = re.findall(
        r"[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{3,4}",
        result
    )


    if matches:

        return matches[0]


    # =====================================================
    # REMOVE COMMON WORDS
    # =====================================================

    result = result.replace(
        "NUMBERPLATE",
        ""
    )

    result = result.replace(
        "NUMBER PLATE",
        ""
    )

    result = result.replace(
        "REGISTRATION",
        ""
    )

    result = result.replace(
        "VEHICLENUMBER",
        ""
    )

    result = result.replace(
        "VEHICLE NUMBER",
        ""
    )

    result = result.replace(
        "PLATE",
        ""
    )


    # =====================================================
    # REMOVE THINK TAGS
    # =====================================================

    result = result.replace(
        "<THINK>",
        ""
    )

    result = result.replace(
        "</THINK>",
        ""
    )


    # =====================================================
    # REMOVE MARKDOWN
    # =====================================================

    result = result.replace(
        "`",
        ""
    )

    result = result.replace(
        "*",
        ""
    )

    result = result.replace(
        "#",
        ""
    )


    # =====================================================
    # SEARCH AGAIN AFTER CLEANING
    # =====================================================

    matches = re.findall(
        r"[A-Z]{2}\s*\d{1,2}\s*[A-Z]{1,3}\s*\d{3,4}",
        result
    )


    if matches:

        plate = re.sub(
            r"[^A-Z0-9]",
            "",
            matches[0]
        )

        return plate


    # =====================================================
    # KEEP ONLY LETTERS AND NUMBERS
    # =====================================================

    result = re.sub(
        r"[^A-Z0-9]",
        "",
        result
    )


    # =====================================================
    # SEARCH PLATE INSIDE CLEANED TEXT
    # =====================================================

    matches = re.findall(
        r"[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{3,4}",
        result
    )


    if matches:

        return matches[0]


    # =====================================================
    # BAD OUTPUT CHECK
    # =====================================================

    bad_outputs = [

        "INEEDTOFOCUSONTHECLEARLYVISIBLELICENSEPLATEOF",

        "FOCUSONTHECLEARLYVISIBLELICENSEPLATE",

        "READTHEVEHICLEREGISTRATIONNUMBERPLATEFROMTHISIMAGE",

        "THEWHITESUVINTHECENTERRIGHTFOREGROUND"

    ]


    if result in bad_outputs:

        return "NOTFOUND"


    # =====================================================
    # FINAL VALIDATION — must look like a real Indian plate
    # =====================================================

    if not re.fullmatch(r"[A-Z]{2}\d{1,2}[A-Z]{1,3}\d{3,4}", result):

        return "NOTFOUND"


    return result

# =========================================================
# GET FINE
# =========================================================

def get_fine(violation):

    conn = sqlite3.connect(
        "Chalan.db"
    )

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT fine
        FROM violations
        WHERE LOWER(violation_name)
        = LOWER(?)
        """,
        (violation,)
    )


    row = cursor.fetchone()

    conn.close()


    if row:

        return row[0]


    return 0


# =========================================================
# GET USER
# =========================================================

def get_user(number_plate):

    conn = sqlite3.connect(
        "user.db"
    )

    cursor = conn.cursor()


    detected_plate = normalize_plate(
        number_plate
    )


    # =====================================================
    # GET ALL USER DETAILS
    # =====================================================

    cursor.execute(
        """
        SELECT
            name,
            vehicle_reg,
            vehicle_type,
            vehnum,
            mobile,
            driver_photo
        FROM users
        """
    )


    rows = cursor.fetchall()

    conn.close()


    # =====================================================
    # FIND MATCH
    # =====================================================

    for row in rows:

        database_plate = normalize_plate(
            row[1]
        )


        if database_plate == detected_plate:

            return row


    return None

# =========================================================
# CHALLAN HISTORY / STATS
# =========================================================

def save_challan(vehicle_reg, violation, fine, plate):

    import datetime

    conn = sqlite3.connect("Chalan.db")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS challans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challan_no TEXT,
            vehicle_reg TEXT,
            violation TEXT,
            fine INTEGER,
            plate TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'Unpaid'
        )
        """
    )

    try:
        conn.execute(
            "ALTER TABLE challans ADD COLUMN status TEXT DEFAULT 'Unpaid'"
        )
    except sqlite3.OperationalError:
        pass

    challan_no = "CHL-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    conn.execute(
        """
        INSERT INTO challans
        (challan_no, vehicle_reg, violation, fine, plate, created_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (challan_no, vehicle_reg, violation, fine, plate,
         datetime.datetime.now().isoformat(), "Unpaid")
    )

    conn.commit()
    conn.close()

    return challan_no


def update_challan_status(challan_no, status):

    conn = sqlite3.connect("Chalan.db")

    conn.execute(
        "UPDATE challans SET status = ? WHERE challan_no = ?",
        (status, challan_no)
    )

    conn.commit()
    conn.close()


def get_stats():

    conn = sqlite3.connect("Chalan.db")

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS challans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challan_no TEXT,
            vehicle_reg TEXT,
            violation TEXT,
            fine INTEGER,
            plate TEXT,
            created_at TEXT,
            status TEXT DEFAULT 'Unpaid'
        )
        """
    )

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(fine) FROM challans")
    total, revenue = cursor.fetchone()

    conn.close()

    return total or 0, revenue or 0

def reset_challans():

    conn = sqlite3.connect("Chalan.db")

    conn.execute("DELETE FROM challans")

    conn.execute(
        "DELETE FROM sqlite_sequence WHERE name = 'challans'"
    )

    conn.commit()
    conn.close()

# =========================================================
# AI CONFIDENCE SCORE
# =========================================================

def get_confidence(image_path, violation):

    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            max_tokens=20,
            temperature=0,
            reasoning_effort="none",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""
Look at this traffic image.

A model predicted the violation as: {violation}

On a scale of 0 to 100, how confident are you that this
image actually shows a "{violation}" violation?

Return ONLY a single integer between 0 and 100.
Do not explain. Do not add text. Do not use markdown.
"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        )
    except RateLimitError:
        return -1

    result = response.choices[0].message.content.strip()

    match = re.search(r"\d+", result)

    if match:
        return max(0, min(100, int(match.group())))

    return 50

# =========================================================
# PDF CHALLAN WITH QR CODE
# =========================================================

def generate_challan_pdf(challan_no, vehicle_reg, violation, fine,
                          name, mobile, plate):

    from fpdf import FPDF
    import qrcode

    temp_dir = os.path.join(os.path.dirname(__file__), "temp")
    os.makedirs(temp_dir, exist_ok=True)

    qr_path = os.path.join(temp_dir, "qr_temp.png")
    qrcode.make("https://echallan.parivahan.gov.in/").save(qr_path)

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "TRAFFIC CHALLAN", ln=True, align="C")

    pdf.set_font("Helvetica", "", 12)
    pdf.ln(5)
    pdf.cell(0, 8, f"Challan No: {challan_no}", ln=True)
    pdf.cell(0, 8, f"Vehicle Registration: {vehicle_reg}", ln=True)
    pdf.cell(0, 8, f"Number Plate: {plate}", ln=True)
    pdf.cell(0, 8, f"Owner Name: {name}", ln=True)
    pdf.cell(0, 8, f"Mobile: {mobile}", ln=True)
    pdf.cell(0, 8, f"Violation: {violation}", ln=True)
    pdf.cell(0, 8, f"Fine Amount: Rs. {fine}", ln=True)
    pdf.cell(0, 8, "Status: Unpaid", ln=True)

    pdf.ln(8)
    pdf.image(qr_path, x=80, w=50)

    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(
        0, 6,
        "Scan the QR code above or visit "
        "https://echallan.parivahan.gov.in/ to verify and pay "
        "this challan on the official government portal."
    )

    return bytes(pdf.output(dest="S"))

# =========================================================
# TEST MODE
# =========================================================

if __name__ == "__main__":

    print()

    print(
        "--------------------------------"
    )

    print(
        "TRAFFIC VIOLATION DETECTION"
    )

    print(
        "--------------------------------"
    )


    test_image = (
        r"images\no_helmet.jpg"
    )


    if not os.path.exists(
        test_image
    ):

        print(
            "Image not found:",
            test_image
        )

        exit()


    # =====================================================
    # VIOLATION
    # =====================================================

    print(
        "Detecting violation..."
    )


    violation = detect_violation(
        test_image
    )


    print(
        "Violation:",
        violation
    )


    # =====================================================
    # FINE
    # =====================================================

    fine = get_fine(
        violation
    )


    print(
        "Fine: ₹",
        fine
    )


    # =====================================================
    # NUMBER PLATE
    # =====================================================

    print(
        "Detecting number plate..."
    )


    number_plate = detect_number_plate(
        test_image
    )


    print(
        "Number Plate:",
        number_plate
    )


    # =====================================================
    # USER
    # =====================================================

    user = get_user(
        number_plate
    )


    if user:

        print()

        print(
            "--------------------------------"
        )

        print(
            "USER FOUND"
        )

        print(
            "--------------------------------"
        )


        print(
            "Name:",
            user[0]
        )

        print(
            "Vehicle:",
            user[1]
        )

        print(
            "Vehicle Type:",
            user[2]
        )

        print(
            "Vehicle Number:",
            user[3]
        )

        print(
            "Mobile:",
            user[4]
        )

        print(
            "Driver Photo:",
            user[5]
        )


    else:

        print()

        print(
            "--------------------------------"
        )

        print(
            "USER NOT FOUND"
        )

        print(
            "--------------------------------"
        )

        print(
            "Number Plate:",
            number_plate
        )

        print(
            "--------------------------------"
        )