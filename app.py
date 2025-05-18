import streamlit as st
import pandas as pd
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import os
from web_scraping import scrape_led_data
from fpdf import FPDF

# ตรวจสอบว่าฟอนต์มีอยู่จริงหรือไม่
FONT_PATH = "NotoSansThai-Regular.ttf"

if not os.path.exists(FONT_PATH):
    st.error("❌ ไม่พบไฟล์ฟอนต์ NotoSansThai-Regular.ttf กรุณาวางไว้ในโฟลเดอร์เดียวกับไฟล์นี้")
else:
    # เริ่มสร้าง PDF
    pdf = FPDF()
    pdf.add_page()
    
    # ✅ ใช้ฟอนต์ภาษาไทยที่รองรับ Unicode
    pdf.add_font("NotoSansThai", "", FONT_PATH, uni=True)
    pdf.set_font("NotoSansThai", size=14)
    
    # ✅ พิมพ์ข้อความไทยได้
    pdf.cell(200, 10, txt="รายงานข้อมูลภาษาไทยจากกรมบังคับคดี", ln=True)

    # ✅ บันทึกไฟล์
    output_path = "thai_report.pdf"
    pdf.output(output_path)

    # ✅ Streamlit แสดงปุ่มดาวน์โหลด
    with open(output_path, "rb") as f:
        st.download_button("📄 ดาวน์โหลด PDF", f, file_name=output_path)
        
# Main application
def main():
    # Page configuration
    st.set_page_config(
        page_title="ระบบข้อมูลทรัพย์กรมบังคับคดี",
        layout="wide",
        initial_sidebar_state="expanded",
        page_icon=None
    )

    # Custom CSS - Google Style
    st.markdown("""
    <style>
        /* Google Style Theme */
        :root {
            --primary-color: #1a73e8;
            --primary-light: #e8f0fe;
            --secondary-color: #5f6368;
            --background-color: #ffffff;
            --surface-color: #f8f9fa;
            --border-color: #dadce0;
            --text-color: #202124;
            --text-secondary: #5f6368;
            --success-color: #188038;
            --warning-color: #f29900;
            --error-color: #d93025;
        }
        
        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-color);
            font-weight: 400;
        }
        
        p, div {
            color: var(--text-color);
            font-weight: 400;
        }
        
        /* Main Header */
        .main-header {
            padding: 1.5rem 0;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 2rem;
        }
        
        .main-header h1 {
            font-size: 1.8rem;
            font-weight: 400;
            color: var(--text-color);
            margin: 0;
        }
        
        .main-header p {
            font-size: 1rem;
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }
        
        /* Section Headers */
        .section-header {
            font-size: 1.2rem;
            font-weight: 500;
            color: var(--text-color);
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-color);
        }
        
        /* Cards */
        .card {
            background-color: var(--background-color);
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 2px 0 rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
            margin-bottom: 1rem;
            height: 100%;
        }
        
        /* Metric Cards */
        .metric-card {
            background-color: var(--background-color);
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 2px 0 rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
            text-align: center;
            height: 100%;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 400;
            color: var(--primary-color);
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }
        
        /* Filter Section */
        .filter-section {
            background-color: var(--surface-color);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
        }
        
        .filter-header {
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-color);
            margin-bottom: 1rem;
        }
        
        /* Results Section */
        .results-section {
            background-color: var(--background-color);
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 1px 2px 0 rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
        }
        
        /* Buttons */
        .stButton>button {
            background-color: var(--primary-color);
            color: white;
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            border: none;
            width: 100%;
            transition: all 0.2s ease;
        }
        
        .stButton>button:hover {
            background-color: #1765cc;
            box-shadow: 0 1px 2px 0 rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
        }
        
        /* Form Elements */
        .stSelectbox>div>div, .stTextInput>div>div>input, .stNumberInput>div>div>input {
            background-color: white;
            border-radius: 4px;
            border: 1px solid var(--border-color);
        }
        
        /* Table */
        .dataframe-container {
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            margin-top: 1rem;
        }
        
        /* Charts */
        .chart-container {
            background-color: white;
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 1px 2px 0 rgba(60, 64, 67, 0.3), 0 1px 3px 1px rgba(60, 64, 67, 0.15);
            margin-bottom: 1.5rem;
        }
        
        .chart-title {
            font-size: 1rem;
            font-weight: 500;
            color: var(--text-color);
            margin-bottom: 0.5rem;
            text-align: center;
        }
        
        /* Info Boxes */
        .info-box {
            background-color: var(--primary-light);
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
            border-left: 4px solid var(--primary-color);
        }
        
        .warning-box {
            background-color: #fef7e0;
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1rem;
            border-left: 4px solid var(--warning-color);
        }
        
        /* Footer */
        footer {
            margin-top: 3rem;
            text-align: center;
            color: var(--text-secondary);
            font-size: 0.875rem;
            padding: 1rem;
            border-top: 1px solid var(--border-color);
        }
        
        /* Streamlit Overrides */
        .stProgress .st-bo {
            background-color: var(--primary-color);
        }
        
        .stAlert {
            border-radius: 8px;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>ระบบข้อมูลทรัพย์กรมบังคับคดี</h1>
        <p>ค้นหา วิเคราะห์ และติดตามข้อมูลทรัพย์จากกรมบังคับคดี</p>
    </div>
    """, unsafe_allow_html=True)

    # Load location data
    @st.cache_data
    def load_location_data():
        try:
            with open("thai_provinces.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback to sample data if file not found
            return [
                {
                    "name_th": "กรุงเทพมหานคร",
                    "name_en": "Bangkok",
                    "amphure": [
                        {
                            "name_th": "พระนคร",
                            "name_en": "Phra Nakhon",
                            "tambon": [
                                {"name_th": "พระบรมมหาราชวัง", "name_en": "Phra Borom Maha Ratchawang"},
                                {"name_th": "วังบูรพาภิรมย์", "name_en": "Wang Burapha Phirom"}
                            ]
                        }
                    ]
                },
                {
                    "name_th": "เชียงใหม่",
                    "name_en": "Chiang Mai",
                    "amphure": [
                        {
                            "name_th": "เมืองเชียงใหม่",
                            "name_en": "Mueang Chiang Mai",
                            "tambon": [
                                {"name_th": "ศรีภูมิ", "name_en": "Si Phum"},
                                {"name_th": "พระสิงห์", "name_en": "Phra Sing"}
                            ]
                        }
                    ]
                }
            ]

    location_data = load_location_data()
    province_names = sorted([p['name_th'] for p in location_data])

    # Initialize session state for storing results
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'search_params' not in st.session_state:
        st.session_state.search_params = {}

    # Filter section
    st.markdown('<div class="section-header">ค้นหาทรัพย์</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["ค้นหาตามพื้นที่", "ค้นหาตามหน่วยงาน"])
        
        with tab1:
            # Create three columns for filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="filter-header">ข้อมูลที่ตั้ง</div>', unsafe_allow_html=True)
                
                selected_province = st.selectbox(
                    "จังหวัด",
                    [""] + province_names,
                    help="เลือกจังหวัดที่ต้องการค้นหาทรัพย์"
                )
                
                # Prepare district and subdistrict lists
                district_display_names = []
                subdistrict_display_names = []
                district_mapping = {}
                subdistrict_mapping = {}
                amphoes = []
                
                if selected_province:
                    amphoes = next((p.get("amphure", []) for p in location_data if p.get("name_th") == selected_province), [])
                    district_mapping = {
                        a["name_th"]: a["name_th"]
                        for a in amphoes
                    }
                    district_display_names = sorted(district_mapping.keys())
                
                selected_district_display = st.selectbox(
                    "อำเภอ",
                    [""] + district_display_names,
                    help="เลือกอำเภอที่ต้องการค้นหาทรัพย์"
                )
                selected_district = district_mapping.get(selected_district_display, "")
                
                tambons = []
                if selected_district:
                    tambons = next(
                        (a.get("tambon", []) for a in amphoes if a["name_th"] == selected_district),
                        []
                    )
                    subdistrict_mapping = {
                        t["name_th"]: t["name_th"]
                        for t in tambons
                    }
                    subdistrict_display_names = sorted(subdistrict_mapping.keys())
                else:
                    subdistrict_mapping = {}
                    subdistrict_display_names = []
                
                selected_subdistrict_display = st.selectbox(
                    "ตำบล",
                    [""] + subdistrict_display_names,
                    help="เลือกตำบลที่ต้องการค้นหาทรัพย์"
                )
                selected_subdistrict = subdistrict_mapping.get(selected_subdistrict_display, "")
            
            with col2:
                st.markdown('<div class="filter-header">ข้อมูลทรัพย์</div>', unsafe_allow_html=True)
                
                asset_type = st.selectbox(
                    "ประเภททรัพย์",
                    ["ทุกประเภท", "บ้าน", "ที่ดิน", "คอนโด", "อาคารพาณิชย์", "ห้องชุด", "ที่ดินพร้อมสิ่งปลูกสร้าง", "ห้องแถว", "อื่นๆ"],
                    help="เลือกประเภททรัพย์ที่ต้องการค้นหา"
                )
                
                col2_1, col2_2 = st.columns(2)
                with col2_1:
                    min_price = st.text_input(
                        "ราคาต่ำสุด (บาท)",
                        placeholder="0",
                        help="ระบุราคาต่ำสุดที่ต้องการค้นหา"
                    )
                with col2_2:
                    max_price = st.text_input(
                        "ราคาสูงสุด (บาท)",
                        placeholder="ไม่จำกัด",
                        help="ระบุราคาสูงสุดที่ต้องการค้นหา"
                    )
                
                st.markdown('<div class="filter-header">ขนาดเนื้อที่</div>', unsafe_allow_html=True)
                col2_3, col2_4, col2_5 = st.columns(3)
                with col2_3:
                    land_rai = st.text_input(
                        "ไร่",
                        placeholder="0",
                        help="ระบุขนาดเนื้อที่ (ไร่)"
                    )
                with col2_4:
                    land_ngan = st.text_input(
                        "งาน",
                        placeholder="0",
                        help="ระบุขนาดเนื้อที่ (งาน)"
                    )
                with col2_5:
                    land_wa = st.text_input(
                        "ตร.วา",
                        placeholder="0",
                        help="ระบุขนาดเนื้อที่ (ตารางวา)"
                    )
            
            with col3:
                st.markdown('<div class="filter-header">ข้อมูลเพิ่มเติม</div>', unsafe_allow_html=True)
                
                auction_date = st.date_input(
                    "วันประมูล",
                    value=None,
                    help="เลือกวันที่ประมูลทรัพย์",
                    format="DD/MM/YYYY"
                )
                
                owner = st.text_input(
                    "ชื่อเจ้าของ",
                    placeholder="ระบุชื่อเจ้าของทรัพย์",
                    help="ระบุชื่อเจ้าของทรัพย์ที่ต้องการค้นหา"
                )
                
                # Add max pages option
                max_pages = st.number_input(
                    "จำนวนหน้าที่ต้องการดึงข้อมูล (0 = ทั้งหมด)",
                    min_value=0,
                    value=5,
                    help="กำหนดจำนวนหน้าที่ต้องการดึงข้อมูล (0 = ดึงทุกหน้า)"
                )
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="filter-header">ข้อมูลหน่วยงาน</div>', unsafe_allow_html=True)
                
                department = st.text_input(
                    "หน่วยงานที่ขาย",
                    placeholder="ระบุชื่อหน่วยงาน",
                    help="ระบุชื่อหน่วยงานที่ขายทรัพย์"
                )
                
                case_number = st.text_input(
                    "หมายเลขคดี",
                    placeholder="ระบุหมายเลขคดี",
                    help="ระบุหมายเลขคดีที่ต้องการค้นหา"
                )
            
            with col2:
                st.markdown('<div class="filter-header">ตัวเลือกเพิ่มเติม</div>', unsafe_allow_html=True)
                
                st.selectbox(
                    "เรียงลำดับตาม",
                    ["ราคาประเมิน (สูง-ต่ำ)", "ราคาประเมิน (ต่ำ-สูง)", "วันที่ประมูล (ล่าสุด)", "วันที่ประมูล (เก่าสุด)"],
                    help="เลือกวิธีการเรียงลำดับผลลัพธ์"
                )
                
                st.checkbox("แสดงเฉพาะทรัพย์ที่มีรูปภาพ", help="เลือกเพื่อแสดงเฉพาะทรัพย์ที่มีรูปภาพประกอบ")
        
        # Search button
        search_col1, search_col2, search_col3 = st.columns([1, 1, 1])
        with search_col2:
            search_button = st.button("ค้นหาทรัพย์", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Process search when button is clicked
    if search_button:
        # Store search parameters
        st.session_state.search_params = {
            "province": selected_province,
            "district": selected_district,
            "subdistrict": selected_subdistrict,
            "asset_type": asset_type,
            "min_price": min_price,
            "max_price": max_price,
            "auction_date": auction_date.strftime("%d/%m/%Y") if auction_date else None,
            "department": department,
            "owner": owner,
            "land_size": {
                "rai": land_rai,
                "ngan": land_ngan,
                "wa": land_wa
            }
        }
        
        # Clean เขต / อำเภอ / ตำบล / แขวง ออกก่อนส่ง
        def clean_district_name(name):
            return name.replace("เขต", "").replace("อำเภอ", "").strip() if name else ""

        def clean_subdistrict_name(name):
            return name.replace("ตำบล", "").replace("แขวง", "").strip() if name else ""

        cleaned_district = clean_district_name(selected_district)
        cleaned_subdistrict = clean_subdistrict_name(selected_subdistrict)
        
        with st.spinner("กำลังดึงข้อมูลจากกรมบังคับคดี..."):
            # Call the scraping function with max_pages parameter and cleaned district/subdistrict
            max_pages_value = None if max_pages == 0 else max_pages
            
            # แสดงค่าที่จะส่งไปยังฟังก์ชัน scrape_led_data เพื่อการ debug
            st.markdown(f"""
            <div class="info-box">
                <strong>กำลังค้นหา:</strong> จังหวัด={selected_province}, อำเภอ={cleaned_district}, ตำบล={cleaned_subdistrict}
            </div>
            """, unsafe_allow_html=True)
            
            df, error = scrape_led_data(selected_province, cleaned_district, cleaned_subdistrict, max_pages_value)
            
            if error:
                st.markdown(f"""
                <div class="warning-box">
                    <strong>เกิดข้อผิดพลาด:</strong> {error}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.session_state.search_results = df
            
    # Display results if available
    if st.session_state.search_results is not None:
        df = st.session_state.search_results
        
        if df.empty:
            st.warning("ไม่พบข้อมูลทรัพย์ตามเงื่อนไขที่ระบุ")
        else:
            st.markdown('<div class="section-header">ผลการค้นหา</div>', unsafe_allow_html=True)
            st.markdown('<div class="results-section">', unsafe_allow_html=True)
            
            # Summary metrics
            st.success(f"พบทรัพย์ทั้งหมด {len(df):,} รายการ")
            
            # Create metrics cards
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{len(df):,}</div>
                    <div class="metric-label">จำนวนรายการทรัพย์ทั้งหมด</div>
                </div>
                """, unsafe_allow_html=True)
            
            with metric_col2:
                try:
                    avg_price = int(df['ราคาประเมิน'].mean())
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{avg_price:,}</div>
                        <div class="metric-label">ราคาประเมินเฉลี่ย (บาท)</div>
                    </div>
                    """, unsafe_allow_html=True)
                except:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value">N/A</div>
                        <div class="metric-label">ราคาประเมินเฉลี่ย (บาท)</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with metric_col3:
                try:
                    most_common_type = df["ประเภททรัพย์"].value_counts().index[0]
                    type_count = df["ประเภททรัพย์"].value_counts().iloc[0]
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{most_common_type}</div>
                        <div class="metric-label">ประเภททรัพย์ที่พบมากที่สุด ({type_count:,} รายการ)</div>
                    </div>
                    """, unsafe_allow_html=True)
                except:
                    st.markdown("""
                    <div class="metric-card">
                        <div class="metric-value">N/A</div>
                        <div class="metric-label">ประเภททรัพย์ที่พบมากที่สุด</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Data visualization
            st.markdown('<div class="section-header">สถิติและการวิเคราะห์ข้อมูล</div>', unsafe_allow_html=True)
            
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">สัดส่วนประเภททรัพย์</div>', unsafe_allow_html=True)
                
                if "ประเภททรัพย์" in df.columns:
                    type_counts = df["ประเภททรัพย์"].value_counts().reset_index()
                    type_counts.columns = ['ประเภททรัพย์', 'จำนวน']
                    
                    fig = px.bar(
                        type_counts, 
                        x='ประเภททรัพย์', 
                        y='จำนวน',
                        color='จำนวน',
                        color_continuous_scale=['#4285F4', '#1A73E8', '#1967D2', '#174EA6'],
                        text='จำนวน'
                    )
                    
                    fig.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(family="Roboto, sans-serif", size=14, color="#5F6368"),
                        margin=dict(l=40, r=40, t=40, b=40),
                        xaxis_title="",
                        yaxis_title="จำนวนรายการ",
                        coloraxis_showscale=False
                    )
                    
                    fig.update_traces(
                        texttemplate='%{text:,}',
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>จำนวน: %{y:,} รายการ'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("ไม่มีข้อมูลประเภททรัพย์")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with chart_col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.markdown('<div class="chart-title">การกระจายตัวตามพื้นที่</div>', unsafe_allow_html=True)
                
                if "ตำบล" in df.columns:
                    location_counts = df["ตำบล"].value_counts().head(10).reset_index()
                    location_counts.columns = ['ตำบล', 'จำนวน']
                    
                    fig = px.bar(
                        location_counts, 
                        x='ตำบล', 
                        y='จำนวน',
                        color='จำนวน',
                        color_continuous_scale=['#4285F4', '#1A73E8', '#1967D2', '#174EA6'],
                        text='จำนวน'
                    )
                    
                    fig.update_layout(
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(family="Roboto, sans-serif", size=14, color="#5F6368"),
                        margin=dict(l=40, r=40, t=40, b=40),
                        xaxis_title="",
                        yaxis_title="จำนวนรายการ",
                        coloraxis_showscale=False
                    )
                    
                    fig.update_traces(
                        texttemplate='%{text:,}',
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>จำนวน: %{y:,} รายการ'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("ไม่มีข้อมูลตำบล")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Price distribution chart
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<div class="chart-title">การกระจายตัวของราคาประเมิน</div>', unsafe_allow_html=True)
            
            if "ราคาประเมิน" in df.columns:
                # Create price ranges
                price_ranges = [
                    (0, 1000000, "ไม่เกิน 1 ล้านบาท"),
                    (1000000, 5000000, "1-5 ล้านบาท"),
                    (5000000, 10000000, "5-10 ล้านบาท"),
                    (10000000, 50000000, "10-50 ล้านบาท"),
                    (50000000, float('inf'), "มากกว่า 50 ล้านบาท")
                ]
                
                price_distribution = []
                for min_price, max_price, label in price_ranges:
                    count = len(df[(df['ราคาประเมิน'] >= min_price) & (df['ราคาประเมิน'] < max_price)])
                    price_distribution.append({"ช่วงราคา": label, "จำนวน": count})
                
                price_df = pd.DataFrame(price_distribution)
                
                fig = px.pie(
                    price_df, 
                    values='จำนวน', 
                    names='ช่วงราคา',
                    color_discrete_sequence=['#4285F4', '#34A853', '#FBBC05', '#EA4335', '#1A73E8'],
                    hole=0.4
                )
                
                fig.update_layout(
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family="Roboto, sans-serif", size=14, color="#5F6368"),
                    margin=dict(l=20, r=20, t=30, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                )
                
                fig.update_traces(
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>จำนวน: %{value:,} รายการ<br>สัดส่วน: %{percent}'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ไม่มีข้อมูลราคาประเมิน")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Data table with improved formatting
            st.markdown('<div class="section-header">รายการทรัพย์ทั้งหมด</div>', unsafe_allow_html=True)
            
            # Format the dataframe for display
            display_df = df.copy()
            
            # Format price column
            if "ราคาประเมิน" in display_df.columns:
                display_df["ราคาประเมิน"] = display_df["ราคาประเมิน"].apply(lambda x: f"{int(x):,} บาท" if pd.notnull(x) else "")
            
            # Display the table with custom styling
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "ราคาประเมิน": st.column_config.TextColumn(
                        "ราคาประเมิน",
                        help="ราคาประเมินของทรัพย์",
                        width="medium",
                    ),
                    "ประเภททรัพย์": st.column_config.TextColumn(
                        "ประเภททรัพย์",
                        width="medium",
                    ),
                    "หมายเลขคดี": st.column_config.TextColumn(
                        "หมายเลขคดี",
                        width="medium",
                    ),
                },
                height=400
            )
            
            # Export options
            st.markdown('<div class="section-header">ส่งออกข้อมูล</div>', unsafe_allow_html=True)
            
            export_col1, export_col2, export_col3 = st.columns(3)
            
            # ปรับปรุงชื่อคอลัมน์ในไฟล์ที่ส่งออก
            export_df = df.copy()
            
            with export_col1:
                csv = export_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    "ดาวน์โหลด CSV",
                    csv,
                    file_name=f"led_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime='text/csv',
                    use_container_width=True
                )
            
            with export_col2:
                # Generate Excel file
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    # Convert the dataframe to an XlsxWriter Excel object
                    export_df.to_excel(writer, sheet_name='ข้อมูลทรัพย์', index=False)
                    
                    # Get the xlsxwriter workbook and worksheet objects
                    workbook = writer.book
                    worksheet = writer.sheets['ข้อมูลทรัพย์']
                    
                    # Add a format for the header cells
                    header_format = workbook.add_format({
                        'bold': True,
                        'text_wrap': True,
                        'valign': 'top',
                        'fg_color': '#D9D9D9',
                        'border': 1
                    })
                    
                    # Write the column headers with the defined format
                    for col_num, value in enumerate(export_df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                        
                    # Set column widths
                    worksheet.set_column('A:K', 15)
                    
                    # Add a number format for the price column
                    money_format = workbook.add_format({'num_format': '#,##0 "บาท"'})
                    
                    # Find the index of the price column
                    if 'ราคาประเมิน' in export_df.columns:
                        price_col_idx = export_df.columns.get_loc('ราคาประเมิน')
                        # Apply the money format to the price column
                        worksheet.set_column(price_col_idx, price_col_idx, 18, money_format)
                
                # Reset buffer position
                buffer.seek(0)
                
                st.download_button(
                    "ดาวน์โหลด Excel",
                    buffer,
                    file_name=f"led_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with export_col3:
                # Generate PDF report using FPDF2 (supports Thai language)
                def create_pdf_with_thai_font():
                    # Create a buffer to store the PDF
                    buffer = io.BytesIO()
                    
                    # Create PDF with FPDF2
                    pdf = FPDF()
                    pdf.add_page()
                    
                    # Try to add a Thai font - FPDF2 has better Unicode support
                    try:
                        # Try to use a Thai font if available
                        pdf.add_font("THSarabun", "", "THSarabun.ttf", uni=True)
                        pdf.set_font("THSarabun", size=16)
                        thai_font_available = True
                    except:
                        # Fallback to DejaVu which has better Unicode support
                        try:
                            pdf.add_font("DejaVu", "", "DejaVuSansCondensed.ttf", uni=True)
                            pdf.set_font("DejaVu", size=12)
                            thai_font_available = True
                        except:
                            # If no Unicode font is available, use English text
                            pdf.set_font("Arial", size=12)
                            thai_font_available = False
                    
                    # Add title and information
                    if thai_font_available:
                        pdf.cell(200, 10, txt="รายงานสรุปผลข้อมูลทรัพย์กรมบังคับคดี", ln=True, align='C')
                        pdf.ln(5)
                        pdf.cell(200, 10, txt=f"จังหวัด: {selected_province or '-'} อำเภอ: {selected_district or '-'} ตำบล: {selected_subdistrict or '-'}", ln=True)
                        pdf.cell(200, 10, txt=f"จำนวนรายการ: {len(df):,}", ln=True)
                        if 'avg_price' in locals():
                            pdf.cell(200, 10, txt=f"ราคาประเมินเฉลี่ย: {avg_price:,} บาท", ln=True)
                    else:
                        # English fallback
                        pdf.cell(200, 10, txt="Property Report from Legal Execution Department", ln=True, align='C')
                        pdf.ln(5)
                        pdf.cell(200, 10, txt=f"Province: {selected_province or '-'} District: {selected_district or '-'} Subdistrict: {selected_subdistrict or '-'}", ln=True)
                        pdf.cell(200, 10, txt=f"Total items: {len(df):,}", ln=True)
                        if 'avg_price' in locals():
                            pdf.cell(200, 10, txt=f"Average price: {avg_price:,} THB", ln=True)
                    
                    pdf.ln(10)
                    
                    # Add a summary table (simplified for compatibility)
                    if len(df) > 0:
                        # Table header
                        if thai_font_available:
                            headers = ['ล��ดับ', 'ล็อตที่-ชุดที่', 'หมายเลขคดี', 'ประเภททรัพย์', 'ราคาประเมิน']
                        else:
                            headers = ['No.', 'Lot-Set', 'Case No.', 'Type', 'Price (THB)']
                        
                        # Set column widths
                        col_widths = [10, 30, 30, 40, 35]
                        
                        # Draw header
                        pdf.set_fill_color(200, 200, 200)
                        for i, header in enumerate(headers):
                            pdf.cell(col_widths[i], 10, header, 1, 0, 'C', True)
                        pdf.ln()
                        
                        # Draw rows (limit to 20 rows for PDF)
                        for i, row in export_df.head(20).iterrows():
                            pdf.cell(col_widths[0], 10, str(i + 1), 1)
                            pdf.cell(col_widths[1], 10, str(row.get('ล็อตที่-ชุดที่', '')), 1)
                            pdf.cell(col_widths[2], 10, str(row.get('หมายเลขคดี', '')), 1)
                            pdf.cell(col_widths[3], 10, str(row.get('ประเภททรัพย์', '')), 1)
                            pdf.cell(col_widths[4], 10, f"{int(row.get('ราคาประเมิน', 0)):,}", 1)
                            pdf.ln()
                    
                    # Output the PDF to the buffer
                    pdf.output(buffer)
                    
                    # Get the value of the buffer
                    pdf_value = buffer.getvalue()
                    buffer.close()
                    
                    return pdf_value
                
                # Create the PDF
                pdf_data = create_pdf_with_thai_font()
                
                st.download_button(
                    "ดาวน์โหลด PDF",
                    pdf_data,
                    file_name=f"led_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            # Email section
            st.markdown('<div class="section-header">ส่งผลลัพธ์ทางอีเมล</div>', unsafe_allow_html=True)
            
            email_col1, email_col2 = st.columns([3, 1])
            with email_col1:
                user_email = st.text_input("อีเมลผู้รับ", placeholder="example@email.com")
            
            with email_col2:
                send_email = st.button("ส่งอีเมล", use_container_width=True)
            
            if send_email:
                if user_email:
                    with st.spinner("กำลังส่งอีเมล..."):
                        try:
                            # Save data to CSV
                            export_df.to_csv("led_data.csv", index=False, encoding='utf-8-sig')
                            
                            # Create email
                            msg = MIMEMultipart()
                            msg["From"] = "your_email@gmail.com"
                            msg["To"] = user_email
                            msg["Subject"] = f"ผลการค้นหาทรัพย์จากกรมบังคับคดี - {datetime.now().strftime('%d/%m/%Y')}"
                            
                            # Add email body
                            email_body = f"""
                            <html>
                            <head>
                                <style>
                                    body {{ font-family: Arial, sans-serif; }}
                                    .header {{ color: #1a73e8; font-size: 18px; font-weight: bold; margin-bottom: 20px; }}
                                    .info {{ margin-bottom: 15px; }}
                                    .footer {{ margin-top: 30px; font-size: 12px; color: #5f6368; }}
                                </style>
                            </head>
                            <body>
                                <div class="header">ผลการค้นหาทรัพย์จากกรมบังคับคดี</div>
                                <div class="info">
                                    <p>จังหวัด: {selected_province or '-'}</p>
                                    <p>อำเภอ: {selected_district or '-'}</p>
                                    <p>ตำบล: {selected_subdistrict or '-'}</p>
                                    <p>จำนวนรายการที่พบ: {len(df):,} รายการ</p>
                                </div>
                                <p>กรุณาดูไฟล์แนบสำหรับรายละเอียดเพิ่มเติม</p>
                                <div class="footer">
                                    <p>ระบบข้อมูลทรัพย์กรมบังคับคดี</p>
                                    <p>ข้อมูล ณ วันที่ {datetime.now().strftime('%d/%m/%Y')}</p>
                                </div>
                            </body>
                            </html>
                            """
                            
                            msg.attach(MIMEText(email_body, 'html'))
                            
                            # Attach CSV file
                            with open("led_data.csv", "rb") as f:
                                part = MIMEBase("application", "octet-stream")
                                part.set_payload(f.read())
                                encoders.encode_base64(part)
                                part.add_header("Content-Disposition", "attachment; filename=led_data.csv")
                                msg.attach(part)
                            
                            # Save data to Excel
                            with pd.ExcelWriter("led_data.xlsx", engine='xlsxwriter') as writer:
                                export_df.to_excel(writer, sheet_name='ข้อมูลทรัพย์', index=False)
                                
                                # Get the xlsxwriter workbook and worksheet objects
                                workbook = writer.book
                                worksheet = writer.sheets['ข้อมูลทรัพย์']
                                
                                # Add a format for the header cells
                                header_format = workbook.add_format({
                                    'bold': True,
                                    'text_wrap': True,
                                    'valign': 'top',
                                    'fg_color': '#D9D9D9',
                                    'border': 1
                                })
                                
                                # Write the column headers with the defined format
                                for col_num, value in enumerate(export_df.columns.values):
                                    worksheet.write(0, col_num, value, header_format)
                                    
                                # Set column widths
                                worksheet.set_column('A:K', 15)
                                
                                # Add a number format for the price column
                                money_format = workbook.add_format({'num_format': '#,##0 "บาท"'})
                                
                                # Find the index of the price column
                                if 'ราคาประเมิน' in export_df.columns:
                                    price_col_idx = export_df.columns.get_loc('ราคาประเมิน')
                                    # Apply the money format to the price column
                                    worksheet.set_column(price_col_idx, price_col_idx, 18, money_format)
                            
                            # Attach Excel file
                            with open("led_data.xlsx", "rb") as f:
                                part = MIMEBase("application", "octet-stream")
                                part.set_payload(f.read())
                                encoders.encode_base64(part)
                                part.add_header("Content-Disposition", "attachment; filename=led_data.xlsx")
                                msg.attach(part)
                            
                            # Create PDF and attach
                            pdf_data = create_pdf_with_thai_font()
                            with open("led_summary.pdf", "wb") as f:
                                f.write(pdf_data)
                                
                            with open("led_summary.pdf", "rb") as f:
                                part = MIMEBase("application", "octet-stream")
                                part.set_payload(f.read())
                                encoders.encode_base64(part)
                                part.add_header("Content-Disposition", "attachment; filename=led_summary.pdf")
                                msg.attach(part)
                            
                            # Send email
                            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                                server.starttls()
                                server.login("your_email@gmail.com", "your_app_password")
                                server.send_message(msg)
                            
                            st.success(f"ส่งอีเมลไปยัง {user_email} เรียบร้อยแล้ว")
                            
                            # Clean up temporary files
                            if os.path.exists("led_data.csv"):
                                os.remove("led_data.csv")
                            if os.path.exists("led_data.xlsx"):
                                os.remove("led_data.xlsx")
                            if os.path.exists("led_summary.pdf"):
                                os.remove("led_summary.pdf")
                                
                        except Exception as e:
                            st.error(f"ส่งอีเมลล้มเหลว: {e}")
                else:
                    st.warning("กรุณาระบุอีเมลผู้รับ")
            
            st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <footer>
        <p>© 2024 ระบบข้อมูลทรัพย์กรมบังคับคดี | พัฒนาโดย Your Company</p>
        <p>ข้อมูลจาก: กรมบังคับคดี กระทรวงยุติธรรม</p>
    </footer>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
