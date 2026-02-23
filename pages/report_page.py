import streamlit as st
import model
from datetime import date
import io
import pandas as pd
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

pdfmetrics.registerFont(TTFont('TH', os.path.join(BASE_DIR, 'THSarabunNew', 'THSarabunNew.ttf')))
pdfmetrics.registerFont(TTFont('TH-Bold', os.path.join(BASE_DIR, 'THSarabunNew', 'THSarabunNew Bold.ttf')))
def render_report():
    st.subheader("📊 รายงานสรุประบบยืม-คืนหนังสือ")


    # =========================
    # 1) กราฟวงกลม : สถานะหนังสือ
    # =========================
    st.markdown("### 1) สัดส่วนหนังสือตามสถานะ")


    status_df = model.get_book_status_summary()


    if status_df.empty:
        st.info("ไม่มีข้อมูลหนังสือ")
    else:
        fig = px.pie(
            status_df,
            names="สถานะหนังสือ",
            values="จำนวน",
            hole=0.4,  # ทำเป็น Donut Chart (ดูเป็น Dashboard มากขึ้น)
            title="สัดส่วนหนังสือตามสถานะ"
        )


        st.plotly_chart(fig, use_container_width=True)


        st.dataframe(status_df, use_container_width=True)


    st.divider()


    # =========================
    # 2) กราฟแท่ง : จำนวนการยืมรายเดือน
    # =========================
    st.markdown("### 2) จำนวนการยืมรายเดือน")


    col1, col2 = st.columns(2)


    with col1:
        month_start = st.date_input(
            "วันที่เริ่มต้น (กราฟรายเดือน)",
            value=date(2025, 6, 1),
            key="month_start"
        )


    with col2:
        month_end = st.date_input(
            "วันที่สิ้นสุด (กราฟรายเดือน)",
            value=date.today(),
            key="month_end"
        )


    if month_start > month_end:
        st.warning("วันที่เริ่มต้นต้องไม่มากกว่าวันที่สิ้นสุด")
        return


    monthly_df = model.get_borrow_summary_by_month(
        month_start.isoformat(),
        month_end.isoformat()
    )


    if monthly_df.empty:
        st.info("ไม่พบข้อมูลการยืมในช่วงเวลาที่เลือก")
    else:
        st.bar_chart(
            monthly_df.set_index("เดือน")["จำนวนการยืม"]
        )


        st.dataframe(monthly_df, use_container_width=True)


    # ===============================
    # 3) รายการผู้ยืม–คืนทั้งหมด
    # ===============================
    st.markdown("### 3) รายการผู้ยืม–คืนทั้งหมด")


    col1, col2, col3 = st.columns(3)


    with col1:
        report_start = st.date_input(
            "วันที่เริ่มต้น (รายงาน)",
            value=date(2025, 6, 1),
            key="report_start"
        )


    with col2:
        report_end = st.date_input(
            "วันที่สิ้นสุด (รายงาน)",
            value=date.today(),
            key="report_end"
        )


    with col3:
        status_label = st.selectbox(
            "สถานะการยืม–คืน",
            ["ทั้งหมด", "ยังไม่คืน", "คืนแล้ว"],
            key="report_status"
        )


    if report_start > report_end:
        st.warning("วันที่เริ่มต้นต้องไม่มากกว่าวันที่สิ้นสุด")
        return


    status_map = {
        "ทั้งหมด": "all",
        "ยังไม่คืน": "borrowed",
        "คืนแล้ว": "returned"
    }


    selected_status = status_map[status_label]


    report_df = model.get_borrow_report(
        report_start.isoformat(),
        report_end.isoformat(),
        selected_status
    )


    if report_df.empty:
        st.info("ไม่พบข้อมูลตามเงื่อนไขที่เลือก")
        return


    st.dataframe(report_df, use_container_width=True)


    # ===============================
    # 4) ส่งออกรายงาน
    # ===============================
    st.markdown("### 4) ส่งออกรายงาน")


    # --- CSV ---
    csv_buffer = io.StringIO()
    report_df.to_csv(csv_buffer, index=False)


    st.download_button(
        label="⬇️ ดาวน์โหลดรายงานผู้ยืม–คืน (CSV)",
        data=csv_buffer.getvalue(),
        file_name="borrow_return_report.csv",
        mime="text/csv"
    )


    # --- Excel ---
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer) as writer:
        report_df.to_excel(writer, index=False, sheet_name="BorrowReport")


    st.download_button(
        label="⬇️ ดาวน์โหลดรายงานผู้ยืม–คืน (Excel)",
        data=excel_buffer.getvalue(),
        file_name="borrow_return_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


    # --- PDF (แนวคิดสำหรับสอนต่อ) ---
    pdf_buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    # แปลง DataFrame -> list
    data = [report_df.columns.tolist()] + report_df.values.tolist()

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),

        # ฟอนต์
        ('FONTNAME', (0,0), (-1,0), 'TH-Bold'),   # header
        ('FONTNAME', (0,1), (-1,-1), 'TH'),       # body

        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
    ]))

    doc.build([table])
    
    st.download_button(
        label="⬇️ ดาวน์โหลดรายงานผู้ยืม–คืน (PDF)",
        data=pdf_buffer.getvalue(),
        file_name="borrow_return_report.pdf",
        mime="application/pdf"
    )
