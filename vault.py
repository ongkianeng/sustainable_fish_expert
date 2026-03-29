import streamlit as st
from PIL import Image, ImageOps, ImageDraw
import time
import io

# --- 1. Streamlit Page Setup ---
st.set_page_config(page_title="Ocean Odyssey Vault", page_icon="🌊", layout="centered")

# CSS for a mobile-first, tech-forward aesthetic
# Custom CSS for Ocean Theme
st.markdown("""
    <style>
    /* Main Theme */
    .stApp { 
        background: linear-gradient(to bottom, #000b1a, #003366); 
        color: white; 
        max_width: 480px; 
        margin: 0 auto;
    }

    /* VAULT STYLE REVERTED */
    [data-testid="stMetricValue"] { 
        color: #00ffff !important; 
        font-family: 'Courier New', monospace; 
        font-weight: bold; 
        font-size: 44px !important; 
    }
    
    .vault-codes { 
        font-family: 'Courier New', monospace; 
        font-size: 28px; 
        font-weight: bold; 
        color: #ffcc00; 
        letter-spacing: 4px; 
        background: rgba(0, 255, 255, 0.1); 
        padding: 8px 12px; 
        border-radius: 8px;
        border: 1px solid rgba(0, 255, 255, 0.2);
        display: inline-block;
        margin-top: 5px;
    }

    /* GRID BUTTONS (Two Rows) */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #00ffff;
        background-color: #000b1a;
        color: #a2d2ff;
        font-weight: normal;
    }

    /* High-Vis Links */
    a { background-color: #ffff00 !important; color: #000 !important; padding: 2px 6px; border-radius: 4px; font-weight: bold; text-decoration: none;}
    
    /* Expander Styling */
    div[data-testid="stExpander"] { background-color: #000b1a !important; border: none !important; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Logic & State ---
if "found_codes_set" not in st.session_state:
    st.session_state.found_codes_set = set()
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "🐠"
if "celebrated" not in st.session_state:
    st.session_state.celebrated = False

# --- Session State Initialization ---
SECRET_CODE = "OCEAN"
SECRET_CODES = set(SECRET_CODE)
# SECRET_CODES = {"O", "C", "E", "A", "N"}
MEMENTO_TARGET_COUNT = len(SECRET_CODES)

if "found_codes_set" not in st.session_state:
    st.session_state.found_codes_set = set()

# --- Square Image Configuration ---
# Output size: 7.5 inches at 300 DPI = 2250x2250 pixels
TARGET_PRINT_SIZE = 2250

# Desired White Border/Matting (e.g., 75 pixels on each side)
# Adjust this value to make the white mask wider or narrower.
BORDER_THICKNESS = 50

def apply_memento(photo_file):
    """Center photo and frame using X/Y coordinate math."""
    
    # --- Step A: Setup Canvas ---
    # Create the white square 'mat'
    canvas = Image.new('RGBA', (TARGET_PRINT_SIZE, TARGET_PRINT_SIZE), 'white')
    
    # --- Step B: Center the Photo ---
    photo_raw = Image.open(photo_file).convert("RGBA")
    photo_inner_size = TARGET_PRINT_SIZE - (BORDER_THICKNESS * 2) # 2100px
    
    # Center-crop the camera feed to a square
    photo_square = ImageOps.fit(
        photo_raw, (photo_inner_size, photo_inner_size), 
        method=Image.Resampling.LANCZOS, centering=(0.5, 0.5)
    )
    
    # Paste photo at (75, 75) - this is mathematically centered on a 2250 canvas
    canvas.paste(photo_square, (BORDER_THICKNESS, BORDER_THICKNESS), photo_square)
    
    try:
        # --- Center the Frame (The X/Y Math) ---
        frame_raw = Image.open("frame.png").convert("RGBA")
        
        # Resize frame to fit the 2250px square
        # 'ImageOps.contain' ensures the whole frame is visible without stretching
        frame_resized = ImageOps.contain(frame_raw, (TARGET_PRINT_SIZE, TARGET_PRINT_SIZE))
        
        # Calculate X and Y offsets to center the frame on the canvas
        frame_w, frame_h = frame_resized.size
        x_offset = (TARGET_PRINT_SIZE - frame_w + 4) // 2
        y_offset = (TARGET_PRINT_SIZE - frame_h + 4) // 2
        
        # Paste the frame using the calculated coordinates
        canvas.alpha_composite(frame_resized, (x_offset, y_offset))
        
        return canvas.convert("RGB") # Final output for print
        
    except FileNotFoundError:
        st.error("Missing frame.png! Returning centered photo only.")
        return canvas.convert("RGB")


st.title("🌊 Ocean Odyssey Vault")
st.write("Complete missions, gather 5 code letters, and unlock the vault! 🔓")

# --- 3. Vault Status ---
current_count = len(st.session_state.found_codes_set)

current_count = len(st.session_state.found_codes_set)
is_unlocked = current_count == 5

# --- 4. Unified Vault Display ---
v_col1, v_col2 = st.columns([1, 2])

with v_col1:
    st.metric(label="Vault Status", value=f"{current_count}/5")

with v_col2:
    # Logic: If all 5 are found, unscramble, otherwise show jumbled letters
    if is_unlocked:
        codes_display = SECRET_CODE
    else:
        found_sorted = sorted(list(st.session_state.found_codes_set))
        codes_display = ", ".join(found_sorted) if found_sorted else "---"
    
    st.metric(label="Codes Unlocked", value=codes_display)

# --- 5. Conditional Unlock Section ---
# Only show the input and button if the vault isn't fully unlocked
if not is_unlocked:
    # st.write("---")
    with st.form("unlock_form", clear_on_submit=True):
        c1, c2 = st.columns([2.5, 1], vertical_alignment="bottom") 

        with c1:
            user_input = st.text_input(
                "Station Code", 
                max_chars=1, 
                placeholder="Type here...", 
                label_visibility="collapsed"
            ).upper().strip()

        with c2:
            # This button now responds to the keyboard 'Enter' key!
            submit_button = st.form_submit_button("Unlock", width="stretch")

        if st.button:
            if user_input in SECRET_CODES:
                if user_input not in st.session_state.found_codes_set:
                    st.session_state.found_codes_set.add(user_input)
                    # Check if this was the final character
                    if len(st.session_state.found_codes_set) == 5:
                        st.balloons()
                    st.rerun()
            elif user_input:
                st.error("Invalid code")

else:
    # st.write("---")
    st.success("🔓 **VAULT ACCESS GRANTED: SYSTEM DECRYPTED** ✨")

# ---------------------------------------------------------
# 📸 SECTION C: FINAL PHOTO MEMENTO (LOCKED UNTIL 5/5)
# ---------------------------------------------------------

if len(st.session_state.found_codes_set) == MEMENTO_TARGET_COUNT:
    st.divider()
    st.header("🎉 Congratulations! Surprise unlocked!")

    # 1. One-time Celebration Logic
    if is_unlocked and not st.session_state.get('celebrated', False):
        st.balloons()
        time.sleep(2) 
        st.session_state.celebrated = True
        st.rerun()
        
    # st.success("🎉 Congratulations!")
    with st.expander("💡 How will you use AI to save our oceans?", expanded=True):
        st.write("View: https://www.youtube.com/shorts/ieiEaV-q3Ck")
    
    # Initialize session state for photo management
    if "photo_taken" not in st.session_state:
        st.session_state.photo_taken = False

    # 2. STATE A: Capture Mode
    if not st.session_state.photo_taken:
        # Toggle for fallback
        use_upload = st.toggle("Camera not working? Use File Upload instead.")
        
        if use_upload:
            photo_input = st.file_uploader("Upload your selfie", type=['jpg', 'png', 'jpeg'])
        else:
            photo_input = st.camera_input("📸 Smile for the AI! Position yourself at the center.")

        if photo_input:
            st.session_state.captured_img_data = photo_input.getvalue()
            st.session_state.photo_taken = True
            st.rerun()

    # 3. STATE B: Result Mode (Camera is hidden)
    else:
        with st.spinner("AI checking gesture... superimposing certified frame..."):
            # Process the image using the standardized centering logic
            final_img = apply_memento(io.BytesIO(st.session_state.captured_img_data))
            
            st.subheader("📸 Ocean of Possibilities: Learning Journey @ Applied AI")
            st.image(final_img, use_container_width=True, caption="Your Photo Memento")
            
            # Action Buttons
            col1, col2 = st.columns(2)
            
            with col1:
                # Prepare high-res download (300 DPI for 7.5" print)
                img_bytes = io.BytesIO()
                final_img.save(img_bytes, format='PNG', dpi=(300, 300))
                
                st.download_button(
                    label="💾 Download Memento",
                    data=img_bytes.getvalue(),
                    file_name="tp_aai_memento.png",
                    mime="image/png",
                    use_container_width=True
                )
            
            with col2:
                # Button to reset state and show the camera again
                if st.button("🔄 Retake Photo", use_container_width=True):
                    st.session_state.photo_taken = False
                    st.rerun()

        st.info("Note: Your photo is not stored on the servers.")

# ---------------------------------------------------------
# 📂 SECTION A: INTERACTIVE MISSION BRIEFING
# ---------------------------------------------------------
with st.expander("📂 Your Missions", expanded=True):
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🐠 What's That Fish?", 
        "🎭 Sea What You Mean", 
        "🎶 Wave or Waste?", 
        "😎 Vibe Check", 
        "💬 Fish Angels Chat"
    ])
    # tab1, tab2, tab3, tab4, tab5 = st.tabs(["🐠", "🎭", "🎶", "😎", "💬"])

    with tab1:
        st.header("**🐠 What's That Fish?**")
        with st.expander("📝 Instructions", expanded=True):
            st.write("1. Follow the instructions of your facilitator. \n" \
                     "2. Sort the fishes into different groups.")
        with st.expander("🎥 Watch Video"):
            st.write("https://www.youtube.com/shorts/rzNondvZCvE")
        with st.expander("💡 Key Takeaways", expanded=True):
            if "N" in st.session_state.found_codes_set:
                st.info("1. AI cannot 'decide' on its own - humans must define labels first. \n" \
                        "2. AI learns specific patterns (e.g., fins, scales) of the object.")
            else:
                st.caption("🔒 Key takeaways locked. Enter the code to reveal.")

    with tab2:
        st.header("**🎭 Sea What You Mean**")
        with st.expander("📝 Instructions", expanded=True):
            st.write("1. Follow the instructions of your facilitator. \n" \
                     "2. Act out the word & guess the word.")
        with st.expander("🎥 Watch Video"):
            st.write("https://www.youtube.com/shorts/VTse_3Puxqs")
        with st.expander("💡 Key Takeaways", expanded=True):
            if "C" in st.session_state.found_codes_set:
                st.info("1. The same word can have multiple meanings. \n" \
                        "2. AI predicts meaning from surrounding words.")
            else:
                st.caption("🔒 Key takeaways locked. Enter the code to reveal.")

    with tab3:
        st.header("**🎶 Wave or Waste?**")
        with st.expander("📝 Instructions", expanded=True):
            st.write("1. Access this site https://teachablemachine.withgoogle.com/train/audio \n" \
                     "2. Use the materials to train the model. \n" \
                     "3. See if AI can correctly detect the sound.")
        with st.expander("🎥 Watch Video"):
            st.write("https://www.linkedin.com/posts/marknewman4_signalprocessing-fouriertransform-voicerecognition-activity-7264904690893549568-Jg1Z")
        with st.expander("💡 Key Takeaways", expanded=True):
            if "O" in st.session_state.found_codes_set:
                st.info("1. AI classifies sound by patterns that can be represented as an image.")
            else:
                st.caption("🔒 Key takeaways locked. Enter the code to reveal.")

    with tab4:
        st.header("**😎 Vibe Check**")
        with st.expander("📝 Instructions", expanded=True):
            st.write("1. Complete the activity in https://studio.code.org/courses/oceans/units/1/lessons/1/levels/8")
        with st.expander("🎥 Watch Video"):
            st.write("https://www.youtube.com/shorts/k_R9JPQyUpw")
        with st.expander("💡 Key Takeaways", expanded=True):
            if "E" in st.session_state.found_codes_set:
                st.info("1. AI reflects the data and labels humans give it. \n" \
                        "2. Bias often comes from missing, unbalanced, or subjective data. \n" \
                        "3. AI can appear confident even when it is wrong.")
            else:
                st.caption("🔒 Key takeaways locked. Enter the code to reveal.")

    with tab5:
        st.header("**💬 Fish Angels Chat**")
        with st.expander("📝 Instructions", expanded=True):
            st.write("1. Complete the activity in https://sustainable-fish-expert.web.app")
        with st.expander("💡 Key Takeaways", expanded=True):
            if "A" in st.session_state.found_codes_set:
                st.info("The chatbot answers questions by: \n" \
                        "1. searching trusted documents (facts about fish & sustainability) \n" \
                        "2. combining that information with language patterns.")
            else:
                st.caption("🔒 Key takeaways locked. Enter the code to reveal.")

