import streamlit as st
import os
import zipfile
from io import BytesIO
from datetime import datetime
from tag_library import tags  # ✅ Make sure you have this file with your master tag list

# --- Week logic ---
def calculate_week_number():
    start = datetime(2024, 12, 30)
    today = datetime.today()
    delta = today - start
    week_num = (delta.days // 7) + 1
    return f"WK{week_num}"

# --- Smart tag matching from filename ---
def generate_auto_descriptors(filename):
    filename = os.path.splitext(filename)[0]  # remove .jpg or .png
    parts = filename.replace("-", "_").replace(" ", "_").split("_")
    parts = [p.strip().lower() for p in parts if p.strip()]

    matched_tags = []
    for tag in tags:
        tag_lower = tag.lower()
        if tag_lower in parts:
            matched_tags.append(tag)
        elif any(tag_lower == "_".join(parts[i:i+2]) for i in range(len(parts)-1)):
            matched_tags.append(tag)

    return matched_tags[:5]

# --- Streamlit UI ---
st.set_page_config(page_title="Nothink Creative Asset Naming", layout="wide")
st.title("✨ Nothink Creative Asset Naming")

uploaded_files = st.file_uploader("📁 Upload Your Assets", accept_multiple_files=True)

st.subheader("📝 Naming Options")

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    product = st.selectbox("Product", ["HARMONIA - HM", "YOURSELFIRST - YF", "DIGESTI - DG"])
    product_code = product.split(" - ")[1]

with col2:
    locale = st.selectbox("Locale", ["English - EN", "Spanish - ES"])
    locale_code = locale.split(" - ")[1]

with col3:
    initials_layout = st.columns([1, 1])
    with initials_layout[0]:
        initials_dropdown = st.selectbox("Initials (preset)", ["", "JB", "LK", "EU", "AY", "KM", "EL"])
    with initials_layout[1]:
        initials_manual = st.text_input("Manual Initials")
    initials = initials_manual if initials_manual else initials_dropdown

col4, col5 = st.columns(2)
with col4:
    start_batch = st.text_input("Starting Batch Number", value="01")
with col5:
    group_size = st.number_input("Assets per batch", value=4, step=1)

creative_manual = st.text_input("✍️ Manual Creative Description (inserted after Asset number)")

col6, col7, col8 = st.columns([1, 1, 1])
with col6:
    format_option = st.selectbox("Format", ["1x1", "16x9", "4x5"])
with col7:
    type_option = st.selectbox("Type", ["Img", "Vid"])
with col8:
    use_smart_naming = st.checkbox("🧠 Add Smart Auto-Naming")

renamed_files = []

if uploaded_files:
    st.markdown("---")
    st.subheader("🔍 Preview & Edit Filenames")

    for i, file in enumerate(uploaded_files):
        colA, colB = st.columns([1, 3])

        ext = os.path.splitext(file.name)[1]
        batch_number = str(int(start_batch) + (i // group_size)).zfill(2)
        asset_number = str((i % group_size) + 1).zfill(2)
        week = calculate_week_number()

        base_folder = f"{product_code}_{locale_code}_{initials}_{week}_{batch_number}"

        name_parts = [
            product_code,
            locale_code,
            initials,
            week,
            batch_number,
            asset_number
        ]

        # --- Combine manual + smart tags cleanly ---
        manual_part = creative_manual.strip().replace(" ", "_")
        auto_parts = generate_auto_descriptors(file.name) if use_smart_naming else []
        combined_parts = [p for p in [manual_part] + auto_parts if p]
        if combined_parts:
            name_parts.append("_".join(combined_parts))

        name_parts.extend([format_option, type_option])
        final_name = "_".join([p for p in name_parts if p]) + ext

        with colA:
            if file.type.startswith("image"):
                st.image(file, width=100)
            elif file.type.startswith("video"):
                st.video(file)
            else:
                st.text(file.name)

        with colB:
            new_name = st.text_input("New name:", value=final_name, key=file.name)
            renamed_files.append((file, new_name, base_folder))

    if st.button("📦 Download Renamed Files"):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for f, new_name, folder in renamed_files:
                zip_path = os.path.join(folder, new_name)
                zipf.writestr(zip_path, f.read())
        st.download_button("⬇️ Download ZIP", data=zip_buffer.getvalue(), file_name="renamed_assets.zip")
