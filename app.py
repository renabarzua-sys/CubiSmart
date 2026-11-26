
import streamlit as st
import math
import csv
import io

# ==========================================
# 1. CONFIGURACION GENERAL
# ==========================================

st.set_page_config(
    page_title="CubiSmart | Cubicación de materiales",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. DISEÑO VISUAL
# ==========================================

st.markdown("""
<style>
    .stApp {
        background:
            radial-gradient(circle at 85% 5%, #D5EEE5 0%, transparent 35%),
            radial-gradient(circle at 5% 80%, #E2EFEC 0%, transparent 35%),
            linear-gradient(135deg, #F5F9F7, #E9F3EF);
        color: #163B39;
    }

    .block-container {
        max-width: 1100px;
        padding: 2rem 3rem 4rem;
    }

    h1, h2, h3 {
        color: #163B39 !important;
        letter-spacing: -0.5px;
    }

    .hero {
        background: linear-gradient(115deg, #124F49, #208C79);
        border-radius: 24px;
        padding: 35px 38px;
        margin-bottom: 25px;
        color: white;
        box-shadow: 0 15px 35px rgba(15, 87, 73, 0.20);
        position: relative;
        overflow: hidden;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        right: -50px;
        top: -80px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 50%;
        pointer-events: none;
    }

    .hero h1 {
        color: white !important;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .hero p {
        color: #D8F3EA;
        font-size: 1.05rem;
        margin-bottom: 0;
    }

    .hero-tag {
        display: inline-block;
        background: rgba(255,255,255,0.13);
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 50px;
        padding: 6px 14px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 16px;
    }

    .section-heading {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 12px 0 18px;
    }

    .section-number {
        background: #DDF3EB;
        color: #127566;
        width: 38px;
        height: 38px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        font-weight: 800;
    }

    .section-title {
        color: #163B39;
        font-size: 1.3rem;
        font-weight: 750;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px;
    }

    div[data-testid="stWidgetLabel"] p {
        color: #315A52 !important;
        font-weight: 600;
    }

    div[data-testid="stNumberInput"] input {
        background-color: #F7FAF9;
        color: #163B39;
        border-radius: 10px;
    }
