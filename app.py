import time
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Dashboard Sensor LDR (Arduino R4 WiFi)",
    page_icon="💡",
    layout="wide",
)

st.title("💡 Dashboard Pemantauan Sensor LDR")
st.caption("Data masa nyata daripada Arduino UNO R4 WiFi → Google Apps Script → Google Sheets → Streamlit")

SHEET_ID = "1_ey2GLl61rOX7FPpwgy1z91OLT1o3GxVPyXD1m6RDjU"
GID = "0"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"

# Kawalan sidebar
st.sidebar.header("Tetapan Dashboard")
bilangan_baris = st.sidebar.slider("Bilangan bacaan terkini dipaparkan", min_value=10, max_value=500, value=50, step=10)
auto_refresh = st.sidebar.checkbox("Auto-refresh setiap 5 saat", value=True)

if st.sidebar.button("Muat Semula Sekarang"):
    st.cache_data.clear()


@st.cache_data(ttl=4)
def muat_data_sheets(url: str) -> pd.DataFrame:
    df = pd.read_csv(url)
    df.columns = [col.strip() for col in df.columns]

    if "Masa" in df.columns:
        df["Masa"] = pd.to_numeric(df["Masa"], errors="coerce")
    if "Nilai LDR" in df.columns:
        df["Nilai LDR"] = pd.to_numeric(df["Nilai LDR"], errors="coerce")

    df = df.dropna(subset=["Masa", "Nilai LDR"]).reset_index(drop=True)
    return df


try:
    df = muat_data_sheets(CSV_URL)

    if df.empty:
        st.warning("Tiada baris data bernombor ditemui dalam Google Sheets buat masa ini.")
    else:
        df_paparan = df.tail(bilangan_baris).copy()

        # Metrik utama
        nilai_terkini = int(df_paparan["Nilai LDR"].iloc[-1])
        nilai_min = int(df_paparan["Nilai LDR"].min())
        nilai_maks = int(df_paparan["Nilai LDR"].max())
        masa_terkini = df_paparan["Masa"].iloc[-1]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Nilai LDR Terkini", nilai_terkini)
        col2.metric("Nilai Minimum", nilai_min)
        col3.metric("Nilai Maksimum", nilai_maks)
        col4.metric("Masa Terkini (s)", f"{masa_terkini:g}")

        st.divider()

        # Graf garis masa nyata
        st.subheader("Graf Perubahan Nilai LDR")
        df_graf = df_paparan.set_index("Masa")[["Nilai LDR"]]
        st.line_chart(df_graf, height=380)

        # Jadual data terkini
        st.subheader("Jadual Data Terkini")
        st.dataframe(df_paparan.iloc[::-1], use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Gagal membaca data daripada Google Sheets: {e}")
    st.info("Pastikan SHEET_ID betul dan tetapan perkongsian Google Sheets ditetapkan kepada 'Anyone with the link' (Viewer).")

if auto_refresh:
    time.sleep(5)
    st.rerun()
