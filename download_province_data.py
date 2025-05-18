import requests
import json

# ✅ ฟังก์ชันดึงข้อมูลจังหวัด-อำเภอ-ตำบล โดยตัดคำว่า "เขต" หรือ "อำเภอ" ออก

def download_province_data():
    url = "https://raw.githubusercontent.com/kongvut/thai-province-data/master/api_province_with_amphure_tambon.json"
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()

        clean_data = []
        for province in data:
            province_name = province["name_th"].strip()
            amphures = []
            for amphure in province.get("amphure", []):
                amphure_name = amphure["name_th"].replace("เขต", "").replace("อำเภอ", "").strip()
                tambons = [
                    {
                        "name_th": tambon["name_th"].replace("ตำบล", "").replace("แขวง", "").strip(),
                        "name_en": tambon["name_en"]
                    }
                    for tambon in amphure.get("tambon", [])
                ]
                amphures.append({
                    "name_th": amphure_name,
                    "name_en": amphure["name_en"],
                    "tambon": tambons
                })
            clean_data.append({
                "name_th": province_name,
                "name_en": province["name_en"],
                "amphure": amphures
            })

        with open("thai_provinces.json", "w", encoding="utf-8") as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)

        print("✅ ดาวน์โหลดและบันทึกไฟล์ thai_provinces.json สำเร็จแล้ว (ตัดเขต/อำเภอ/ตำบล ออก)")

    except requests.exceptions.RequestException as e:
        print("❌ ไม่สามารถดาวน์โหลดข้อมูลได้:", e)

if __name__ == "__main__":
    download_province_data()
