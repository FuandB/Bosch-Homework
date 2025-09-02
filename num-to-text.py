import re
import streamlit as st

# ====== Core: number -> Vietnamese text ======
NUMBERS = {
    0: "không", 1: "một", 2: "hai", 3: "ba", 4: "bốn",
    5: "năm", 6: "sáu", 7: "bảy", 8: "tám", 9: "chín"
}

def scale_name(i: int) -> str:
    """
    i theo nhóm 3 chữ số (từ phải sang trái):
    0:"", 1:"nghìn", 2:"triệu", 3:"tỷ", 4:"nghìn tỷ", 5:"triệu tỷ", 6:"tỷ tỷ", ...
    """
    if i == 0:
        return ""
    base_map = {1: "nghìn", 2: "triệu", 0: ""}
    base = base_map[i % 3]
    ty_repeat = i // 3
    parts = []
    if base:
        parts.append(base)
    if ty_repeat > 0:
        parts += ["tỷ"] * ty_repeat
    return " ".join(parts).strip()

def read_triplet(n: int, full: bool) -> str:
    tram = n // 100
    chuc = (n // 10) % 10
    donvi = n % 10
    parts = []

    if tram > 0:
        parts += [NUMBERS[tram], "trăm"]
    elif full and (chuc > 0 or donvi > 0):
        parts += ["không", "trăm"]

    if chuc > 1:
        parts += [NUMBERS[chuc], "mươi"]
        if donvi == 1:
            parts.append("mốt")
        elif donvi == 4:
            parts.append("tư")
        elif donvi == 5:
            parts.append("lăm")
        elif donvi != 0:
            parts.append(NUMBERS[donvi])
    elif chuc == 1:
        parts.append("mười")
        if donvi == 5:
            parts.append("lăm")
        elif donvi != 0:
            parts.append(NUMBERS[donvi])
    else:
        if donvi != 0:
            if tram != 0 or full:
                parts.append("lẻ")
            parts.append(NUMBERS[donvi])

    return " ".join(parts).strip()

def number_to_vietnamese(n: int) -> str:
    if n == 0:
        return "không"
    if n < 0:
        return "âm " + number_to_vietnamese(-n)

    triplets = []
    x = n
    while x > 0:
        triplets.append(x % 1000)
        x //= 1000

    parts = []
    for i in range(len(triplets) - 1, -1, -1):
        trip = triplets[i]
        if trip != 0:
            full = (i != len(triplets) - 1)
            chunk = read_triplet(trip, full)
            scale = scale_name(i)
            parts.append(chunk + (" " + scale if scale else ""))

    return " ".join(parts).replace("  ", " ").strip()

def parse_int(s: str):
    """
    Chấp nhận: dấu cách, dấu phẩy, dấu chấm ngăn cách, dấu +/-
    Loại bỏ mọi ký tự không phải [0-9-+] và giữ duy nhất dấu âm ở đầu nếu có.
    """
    s = s.strip()
    if not s:
        return None
    # Cho phép dấu - hoặc + ở đầu; bỏ mọi thứ khác không phải digit
    sign = ""
    if s[0] in "+-":
        sign = s[0]
        s = s[1:]
    digits = re.sub(r"[^0-9]", "", s)
    if digits == "":
        return None
    try:
        return int(sign + digits)
    except ValueError:
        return None

# ====== UI ======
st.set_page_config(page_title="Finn Bành", page_icon="https://cdn.iconscout.com/icon/free/png-256/free-bosch-logo-icon-svg-png-download-2875346.png")
st.title("🔢 Number → Vietnamese text (VN đọc số)")

st.write("Please enter an integer number")

# Dùng form để nhấn Enter hoạt động như submit
with st.form("convert_form", clear_on_submit=False):
    user_input = st.text_input("Số cần đọc", value="", placeholder="Ví dụ: 123456789")
    submitted = st.form_submit_button("Enter / Convert")

# Xử lý khi bấm nút
if submitted:
    n = parse_int(user_input)
    if n is None:
        st.error("Giá trị không hợp lệ. Hãy nhập số nguyên (có thể có dấu âm, dấu phẩy/dấu cách).")
    else:
        result = number_to_vietnamese(n)
        st.success("Kết quả:")
        st.text_area("Output", value=result, height=100)
        # gợi ý ví dụ nhanh
        # with st.expander("Ví dụ nhanh"):
        #     examples = [0, 5, 10, 15, 24, 105, 1005, 123456789, 10**12, 10**15, 10**18, -123456]
        #     demo = "\n".join(f"{x} → {number_to_vietnamese(x)}" for x in examples)
        #     st.code(demo, language="text")
