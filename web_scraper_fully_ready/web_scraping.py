import requests
import json
import pandas as pd
import re
import streamlit as st
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

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

# ✅ ฟังก์ชันดึงข้อมูลทรัพย์จากเว็บไซต์กรมบังคับคดี
def scrape_led_data(province='', district='', subdistrict='', max_pages=None):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # ตัดคำนำหน้าออกก่อนส่งไปยังเว็บไซต์
    cleaned_district = district.replace("เขต", "").replace("อำเภอ", "").strip() if district else ""
    cleaned_subdistrict = subdistrict.replace("ตำบล", "").replace("แขวง", "").strip() if subdistrict else ""
    
    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 30)  # เพิ่มเวลารอเป็น 30 วินาที
        driver.get('https://asset.led.go.th/newbidreg/default.asp')
        
        # Debug: แสดงค่าที่จะส่งไปยังเว็บไซต์
        print(f"DEBUG: จังหวัด={province}, อำเภอ={cleaned_district}, ตำบล={cleaned_subdistrict}")

        if province:
            province_input = wait.until(EC.presence_of_element_located((By.NAME, 'province')))
            province_input.clear()
            province_input.send_keys(province)
            time.sleep(3)  # เพิ่มเวลารอเป็น 3 วินาที

        if cleaned_district:
            district_input = wait.until(EC.presence_of_element_located((By.NAME, 'ampur')))
            district_input.clear()
            district_input.send_keys(cleaned_district)  # ส่งค่าที่ตัดคำนำหน้าออกแล้ว
            time.sleep(3)  # เพิ่มเวลารอเป็น 3 วินาที
            
            # ลองใช้ JavaScript Executor หากวิธีปกติไม่ทำงาน
            try:
                driver.execute_script(f"document.getElementsByName('ampur')[0].value = '{cleaned_district}';")
                time.sleep(1)
            except Exception as js_error:
                print(f"DEBUG: JS Error for district: {js_error}")

        if cleaned_subdistrict:
            subdistrict_input = wait.until(EC.presence_of_element_located((By.NAME, 'tumbol')))
            subdistrict_input.clear()
            subdistrict_input.send_keys(cleaned_subdistrict)  # ส่งค่าที่ตัดคำนำหน้าออกแล้ว
            time.sleep(3)  # เพิ่มเวลารอเป็น 3 วินาที
            
            # ลองใช้ JavaScript Executor หากวิธีปกติไม่ทำงาน
            try:
                driver.execute_script(f"document.getElementsByName('tumbol')[0].value = '{cleaned_subdistrict}';")
                time.sleep(1)
            except Exception as js_error:
                print(f"DEBUG: JS Error for subdistrict: {js_error}")

        captcha_text = wait.until(EC.presence_of_element_located((By.XPATH, '//font[@color="blue"]'))).text.strip()
        driver.find_element(By.NAME, 'seckey').send_keys(captcha_text)
        
        # บันทึกภาพหน้าจอก่อนคลิกปุ่มค้นหา
        driver.save_screenshot("before_search.png")
        
        # คลิกปุ่มค้นหาและรอให้ผลลัพธ์แสดง
        search_button = wait.until(EC.element_to_be_clickable((By.NAME, 'search')))
        search_button.click()
        time.sleep(7)  # เพิ่มเวลารอเป็น 7 วินาที
        
        # บันทึกภาพหน้าจอหลังคลิกปุ่มค้นหา
        driver.save_screenshot("after_search.png")

        try:
            # รอให้ตารางผลลัพธ์ปรากฏ
            wait.until(EC.presence_of_element_located((By.XPATH, '//table[@class="table linkevent"]')))
        except TimeoutException:
            return pd.DataFrame(), "ไม่พบข้อมูลทรัพย์ตามเงื่อนไขที่ระบุ หรือเว็บไซต์ไม่ตอบสนอง"

        try:
            pagination_text = driver.find_element(By.XPATH, '//div[contains(text(), "หน้าที่")]').text
            total_pages = int(re.search(r'(\d+)/(\d+)', pagination_text).group(2))
            st.info(f"พบข้อมูลทั้งหมด {total_pages} หน้า")
        except (NoSuchElementException, AttributeError):
            total_pages = 1
            st.info("พบข้อมูล 1 หน้า")

        if max_pages is not None and max_pages < total_pages:
            total_pages = max_pages
            st.info(f"จะดึงข้อมูลเพียง {max_pages} หน้าตามที่กำหนด")

        all_data = []
        current_page = 1
        progress_bar = st.progress(0)
        status_text = st.empty()

        while current_page <= total_pages:
            status_text.text(f"กำลังดึงข้อมูลหน้า {current_page}/{total_pages}")
            progress_bar.progress(current_page / total_pages)
            try:
                # รอให้ตารางปรากฏในหน้าปัจจุบัน
                table = wait.until(EC.presence_of_element_located((By.XPATH, '//table[@class="table linkevent"]')))
                rows = table.find_elements(By.TAG_NAME, 'tr')
                
                # ข้ามแถวแรกซึ่งเป็นส่วนหัวตาราง
                for row in rows[1:]:
                    try:
                        cols = row.find_elements(By.TAG_NAME, 'td')
                        if len(cols) >= 10:  # ตรวจสอบว่ามีคอลัมน์เพียงพอหรือไม่
                            # ดึงข้อมูลตามคอลัมน์ในตาราง (ตามโครงสร้างจริงของเว็บไซต์)
                            order_number = cols[0].text.strip()  # ลำดับ
                            lot_set = cols[1].text.strip()  # ล็อตที่-ชุดที่
                            case_number = cols[2].text.strip()  # หมายเลขคดี
                            property_type = cols[3].text.strip()  # ประเภททรัพย์
                            
                            # ขนาดที่ดิน (แยกเป็น 3 คอลัมน์)
                            rai = cols[4].text.strip() or "0"  # ไร่
                            ngan = cols[5].text.strip() or "0"  # งาน
                            sq_wa = cols[6].text.strip() or "0"  # ตร.วา
                            
                            # ราคาประเมิน
                            price = cols[7].text.strip()
                            
                            # ที่ตั้ง
                            subdistrict = cols[8].text.strip()  # ตำบล
                            district = cols[9].text.strip()  # อำเภอ
                            province = cols[10].text.strip() if len(cols) > 10 else ""  # จังหวัด
                            
                            # เก็บข้อมูลในรูปแบบลิสต์
                            row_data = [
                                order_number, lot_set, case_number, property_type,
                                rai, ngan, sq_wa, price, subdistrict, district, province
                            ]
                            all_data.append(row_data)
                    except Exception as row_error:
                        st.warning(f"ข้อผิดพลาดในการดึงข้อมูลแถว: {row_error}")
                        continue

                if current_page < total_pages:
                    next_page_found = False
                    
                    # วิธีที่ 1: คลิกที่หมายเลขหน้าถัดไป
                    try:
                        next_page_number = current_page + 1
                        next_page_link = driver.find_element(By.XPATH, f'//a[text()="{next_page_number}"]')
                        next_page_link.click()
                        next_page_found = True
                        time.sleep(5)  # รอให้หน้าโหลด
                    except NoSuchElementException:
                        pass
                    
                    # วิธีที่ 2: คลิกที่ปุ่ม "»" (หน้าถัดไป)
                    if not next_page_found:
                        try:
                            next_button = driver.find_element(By.XPATH, '//a[contains(text(), "»")]')
                            next_button.click()
                            next_page_found = True
                            time.sleep(5)  # รอให้หน้าโหลด
                        except NoSuchElementException:
                            pass
                    
                    # วิธีที่ 3: ใช้ JavaScript เพื่อเปลี่ยนหน้า
                    if not next_page_found:
                        try:
                            driver.execute_script(f"goToPage({next_page_number});")
                            next_page_found = True
                            time.sleep(5)  # รอให้หน้าโหลด
                        except Exception:
                            pass
                    
                    if not next_page_found:
                        st.warning(f"ไม่สามารถไปยังหน้าถัดไปได้ หยุดที่หน้า {current_page}")
                        break
                
                current_page += 1
            except Exception as page_error:
                st.error(f"เกิดข้อผิดพลาดในการดึงข้อมูลหน้า {current_page}: {page_error}")
                break

        progress_bar.empty()
        status_text.empty()

        # กำหนดชื่อคอลัมน์ให้ตรงกับเว็บไซต์
        columns = [
            'ลำดับ', 'ล็อตที่-ชุดที่', 'หมายเลขคดี', 'ประเภททรัพย์',
            'ไร่', 'งาน', 'ตร.วา', 'ราคาประเมิน', 'ตำบล', 'อำเภอ', 'จังหวัด'
        ]
        df = pd.DataFrame(all_data, columns=columns)

        # แปลงคอลัมน์ตัวเลขให้เป็นตัวเลข
        numeric_cols = ['ไร่', 'งาน', 'ตร.วา']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # แปลงคอลัมน์ราคาประเมินให้เป็นตัวเลข
        df['ราคาประเมิน'] = df['ราคาประเมิน'].str.replace(',', '').str.replace(' บาท', '').str.replace('บาท', '')
        df['ราคาประเมิน'] = pd.to_numeric(df['ราคาประเมิน'], errors='coerce')

        return df, None

    except Exception as e:
        if driver:
            try:
                screenshot_path = "error_screenshot.png"
                driver.save_screenshot(screenshot_path)
                st.error(f"เกิดข้อผิดพลาด: {e}")
                st.image(screenshot_path, caption="สถานะหน้าเว็บเมื่อเกิดข้อผิดพลาด")
            except:
                pass
        return pd.DataFrame(), f"เกิดข้อผิดพลาด: {str(e)}"

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    download_province_data()
