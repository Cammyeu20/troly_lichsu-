import streamlit as st
from gtts import gTTS
from io import BytesIO
import base64
import streamlit.components.v1 as components

# ======================
# ⚙️ CẤU HÌNH TRANG
# ======================
st.set_page_config(page_title="Trợ lý Lịch sử", layout="centered")

# ======================
# 🧠 KHỞI TẠO CLIENT AI
# ======================
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def tra_loi_ai(cau_hoi):
    """Gọi GPT-4o-mini để trả lời lịch sử."""
    prompt = f"""
    Bạn là chuyên gia lịch sử. 
    Trả lời thật chính xác, ngắn gọn, dễ hiểu (2–4 câu).
    Câu hỏi: {cau_hoi}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message["content"]

if "audio_unlocked" not in st.session_state:
    st.session_state["audio_unlocked"] = False

# ======================
# 🧠 KHỞI TẠO TRẠNG THÁI
# ======================
st.title("📚 TRỢ LÝ LỊCH SỬ")
st.write("👉 Bấm **BẬT ÂM THANH** (chỉ 1 lần), sau đó nhập câu hỏi rồi bấm **Trả lời**.")
st.write("📱 Trên hệ điều hành IOS, bạn cần bấm nút ▶ để nghe giọng nói (quy định của Safari).")
st.write("📱 Trên hệ điều hành android,máy tính bảng,laptop,máy tính bàn không cần bấm nút ▶ để nghe vì nó tự nói .")
# ======================
# 🔓 NÚT BẬT ÂM THANH
# ======================
if st.button("🔊 BẬT ÂM THANH (1 lần)"):
    js_unlock = """
    <script>
      try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        if (ctx.state === 'suspended') ctx.resume();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        gain.gain.value = 0;
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.05);
        console.log("Âm thanh đã mở khoá thành công.");
      } catch(e) {
        console.log("Không thể mở khoá âm thanh:", e);
      }
    </script>
    """
    components.html(js_unlock, height=0)
    st.session_state["audio_unlocked"] = True
    st.success("✅ Âm thanh đã được bật (PC, Android, MacBook).")

# ======================
# 📜 DỮ LIỆU LỊCH SỬ
# ======================

# ======================
# 💬 GIAO DIỆN NGƯỜI DÙNG
# ======================
cau_hoi = st.text_input("❓ Nhập câu hỏi lịch sử:")

if st.button("📖 Trả lời"):
    tra_loi = tra_loi_lich_su(cau_hoi)
# ⭐ Trả lời bằng AI thay vì dữ liệu cố định
    st.success(tra_loi)

    # 🎙️ TẠO GIỌNG NÓI
    try:
        mp3_fp = BytesIO()
        gTTS(text=tra_loi, lang="vi").write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio_b64 = base64.b64encode(mp3_fp.read()).decode()
    except Exception as e:
        st.error(f"Lỗi tạo giọng nói: {e}")
        audio_b64 = None

    if audio_b64:
        autoplay_flag = "true" if st.session_state["audio_unlocked"] else "false"
        audio_html = f"""
        <div id="tts_player"></div>
        <script>
        (function() {{
            const isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent);
            const unlocked = {autoplay_flag};
            const player = document.createElement('audio');
            player.src = "data:audio/mp3;base64,{audio_b64}";
            player.controls = true;
            player.playsInline = true;
            document.getElementById("tts_player").appendChild(player);
            
            if (!isIOS && unlocked) {{
                player.autoplay = true;
                player.play().catch(e => console.log("Autoplay bị chặn:", e));
            }}
        }})();
        </script>
        """
        components.html(audio_html, height=100)

        # 🧭 Thông báo phù hợp với tất cả các thiết bị
        if st.session_state["audio_unlocked"]:
            st.info("🔊 Thiết bị này sẽ tự động phát (Android, PC, Mac.,,,).")
        else:
            st.warning("⚠️ Trên iPhone: bấm ▶ để nghe.")
