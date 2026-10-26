import streamlit as st
import pandas as pd
import re
import io

# Try importing PDF libraries
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False


# ==========================================
# CORE .STG FORMATTING ENGINE & TEMPLATES
# ==========================================

def make_row(justification: str, caption: str, bright: int = 46, speed: int = 46) -> dict:
    return {
        "Justification": justification,
        "Bright": bright,
        "Speed": speed,
        "Caption": caption
    }

def make_blanks(count: int, justification: str = "Left", bright: int = 46, speed: int = 46) -> list:
    return [make_row(justification, "", bright, speed) for _ in range(count)]

def get_header_rows(show_name: str, captioner_info: str, font_size: str = "LGE", bright: int = 46, speed: int = 46) -> list:
    rows = []
    # Lines 1-6: 6 blank Left lines
    rows.extend(make_blanks(6, "Left", bright, speed))
    # Lines 7-10: CO setup block
    rows.append(make_row("Left", "CO:  leave 3 lines at beginning / end ", bright, speed))
    rows.append(make_row("Left", "CO:  in case of emergencies!", bright, speed))
    rows.append(make_row("Left", f"CO:  FONT SIZE: {font_size}", bright, speed))
    rows.append(make_row("Left", f"CO:  last captioned by ... {captioner_info}", bright, speed))
    # Lines 11-13: 3 blank Left lines
    rows.extend(make_blanks(3, "Left", bright, speed))
    # Lines 14-16: Show intro
    rows.append(make_row("Centre", "This evening's performance", bright, speed))
    rows.append(make_row("Centre", f"of {show_name}", bright, speed))
    rows.append(make_row("Centre", "is being captioned.", bright, speed))
    # Lines 17-19: 3 blank Centre lines
    rows.extend(make_blanks(3, "Centre", bright, speed))
    # Lines 20-21
    rows.append(make_row("Centre", "If you miss a word during the show", bright, speed))
    rows.append(make_row("Centre", "the captions are there to help you.", bright, speed))
    # Lines 22-24: 3 blank Left lines
    rows.extend(make_blanks(3, "Left", bright, speed))
    # Lines 25-27
    rows.append(make_row("Centre", "Captioning gives deaf, deafened", bright, speed))
    rows.append(make_row("Centre", "and hard of hearing people", bright, speed))
    rows.append(make_row("Centre", "access to the performance.", bright, speed))
    # Lines 28-30: 3 blank Centre lines
    rows.extend(make_blanks(3, "Centre", bright, speed))
    # Lines 31-33
    rows.append(make_row("Centre", "Captions may also be helpful", bright, speed))
    rows.append(make_row("Centre", "to those who are neurodivergent or", bright, speed))
    rows.append(make_row("Centre", "for whom English is a second language.", bright, speed))
    # Lines 34-36: 3 blank Left lines
    rows.extend(make_blanks(3, "Left", bright, speed))
    # Lines 37-39
    rows.append(make_row("Centre", "Please may we remind you", bright, speed))
    rows.append(make_row("Centre", "to turn off all mobile phones", bright, speed))
    rows.append(make_row("Centre", "while in the theatre.  Thank you.", bright, speed))
    # Lines 40-43: 4 blank Left lines
    rows.extend(make_blanks(4, "Left", bright, speed))
    return rows

def get_interval_rows(bright: int = 46, speed: int = 46) -> list:
    rows = []
    rows.append(make_row("Left", "CO: BLACKOUT", bright, speed))
    rows.extend(make_blanks(4, "Left", bright, speed))
    rows.append(make_row("Centre", "INTERVAL", bright, speed))
    rows.extend(make_blanks(4, "Centre", bright, speed))
    rows.append(make_row("Centre", "Please may we remind you", bright, speed))
    rows.append(make_row("Centre", "to turn back off all mobile phones", bright, speed))
    rows.append(make_row("Centre", "while in the theatre.  Thank you.", bright, speed))
    rows.extend(make_blanks(3, "Left", bright, speed))
    rows.append(make_row("Centre", "We'd love to hear your feedback!", bright, speed))
    rows.append(make_row("Centre", "Please tell a member of staff", bright, speed))
    rows.append(make_row("Centre", "if you're enjoying having captions.", bright, speed))
    rows.extend(make_blanks(3, "Centre", bright, speed))
    rows.append(make_row("Centre", "^  ENTR'ACTE", bright, speed))
    rows.extend(make_blanks(4, "Left", bright, speed))
    return rows

def get_footer_rows(bright: int = 46, speed: int = 46) -> list:
    rows = []
    rows.extend(make_blanks(5, "Left", bright, speed))
    rows.append(make_row("Left", "Next captioned performance:", bright, speed))
    rows.extend(make_blanks(3, "Left", bright, speed))
    rows.append(make_row("Left", "Emergency messages", bright, speed))
    rows.extend(make_blanks(3, "Left", bright, speed))
    
    # Tech stop
    rows.append(make_row("Left", "We have a technical problem", bright, speed))
    rows.append(make_row("Left", "and need to stop the performance", bright, speed))
    rows.append(make_row("Left", "for a few minutes.", bright, speed))
    rows.append(make_row("Left", "Thank you.", bright, speed))
    rows.extend(make_blanks(3, "Left", bright, speed))
    
    # Tech delay
    rows.append(make_row("Left", "We have a technical problem", bright, speed))
    rows.append(make_row("Left", "and need to delay the performance", bright, speed))
    rows.append(make_row("Left", "for a few minutes.", bright, speed))
    rows.append(make_row("Left", "Thank you.", bright, speed))
    rows.extend(make_blanks(3, "Left", bright, speed))
    
    # Security 1
    rows.append(make_row("Left", "Security alert.", bright, speed))
    rows.append(make_row("Left", "Please could you leave the auditorium?", bright, speed))
    rows.append(make_row("Left", "Thank you.", bright, speed))
    rows.extend(make_blanks(3, "Left", bright, speed))
    
    # Security 2
    rows.append(make_row("Left", "Security alert.", bright, speed))
    rows.append(make_row("Left", "Please could you leave the theatre?", bright, speed))
    rows.append(make_row("Left", "Thank you.", bright, speed))
    rows.extend(make_blanks(3, "Left", bright, speed))
    
    # Security 3
    rows.append(make_row("Left", "Security alert.", bright, speed))
    rows.append(make_row("Left", "Please could you follow the ushers", bright, speed))
    rows.append(make_row("Left", "and leave the auditorium as quickly and ", bright, speed))
    rows.append(make_row("Left", "calmly as possible?", bright, speed))
    rows.append(make_row("Left", "Thank you.", bright, speed))
    rows.extend(make_blanks(3, "Left", bright, speed))
    
    # Security 4
    rows.append(make_row("Left", "Security alert.", bright, speed))
    rows.append(make_row("Left", "Please could you follow the ushers", bright, speed))
    rows.append(make_row("Left", "and leave the building as quickly", bright, speed))
    rows.append(make_row("Left", "and calmly as possible?", bright, speed))
    rows.append(make_row("Left", "Thank you.", bright, speed))
    rows.extend(make_blanks(3, "Left", bright, speed))
    
    # About to begin
    rows.append(make_row("Left", "The performance is about to begin.", bright, speed))
    rows.extend(make_blanks(10, "Left", bright, speed))
    return rows


# ==========================================
# TEXT NORMALIZATION & SMART WRAPPING
# ==========================================

def format_punctuation(text: str) -> str:
    """Applies Stagetext punctuation rules: spaced ellipses and double spaces after mid-line periods."""
    text = re.sub(r'(\.\s*\.+\s*\.+\.|…)', ' . . . ', text)
    text = re.sub(r'\s+\.\s+\.\s+\.\s*', ' . . . ', text)
    text = re.sub(r'[ \t]+', ' ', text).strip()
    text = re.sub(r'([.!?])\s+([A-Z])', r'\1  \2', text)
    return text

def smart_wrap_stg(text: str, max_chars: int = 38, first_line_prefix: str = "") -> list:
    full_first = f"{first_line_prefix}{text}".strip()
    if len(full_first) <= max_chars:
        return [full_first]

    words = text.split(' ')
    lines = []
    current_prefix = first_line_prefix
    current_words = []

    for word in words:
        if not word:
            continue
        candidate_words = current_words + [word]
        candidate_line = current_prefix + " ".join(candidate_words)
        candidate_line = re.sub(r'([.!?]) ([A-Z])', r'\1  \2', candidate_line)

        if len(candidate_line) <= max_chars:
            current_words.append(word)
        else:
            if current_words:
                break_idx = None
                if len(current_words) >= 4:
                    for i in range(len(current_words) - 1, max(1, len(current_words) // 2) - 1, -1):
                        w = current_words[i]
                        if w.endswith((',', ';', ':', '-', '—')) or w == '.':
                            break_idx = i + 1
                            break
                if break_idx:
                    emit_words = current_words[:break_idx]
                    leftover_words = current_words[break_idx:]
                    line_str = current_prefix + " ".join(emit_words)
                    line_str = re.sub(r'([.!?]) ([A-Z])', r'\1  \2', line_str)
                    lines.append(line_str)
                    current_prefix = ""
                    current_words = leftover_words + [word]
                else:
                    line_str = current_prefix + " ".join(current_words)
                    line_str = re.sub(r'([.!?]) ([A-Z])', r'\1  \2', line_str)
                    lines.append(line_str)
                    current_prefix = ""
                    current_words = [word]
            else:
                lines.append(candidate_line)
                current_prefix = ""
                current_words = []

    if current_words:
        line_str = current_prefix + " ".join(current_words)
        line_str = re.sub(r'([.!?]) ([A-Z])', r'\1  \2', line_str)
        lines.append(line_str)

    return lines


# ==========================================
# SCRIPT PARSER
# ==========================================

SPEAKER_REGEX = re.compile(
    r"^(\+\s*)?([A-Z][A-Z0-9\s'\.\-&/]{1,28}?)(?:\s*\(([^\)]+)\))?\s*:\s*(.*)$"
)

PAGE_MARKER_REGEX = re.compile(r'^(?:PAGE|PG\.?|P\.?)\s*(\d+)(?:\s*(?:OF|/)\s*(\d+))?$', re.IGNORECASE)

def parse_script_to_stg(
    raw_text: str,
    max_chars: int = 38,
    bright: int = 46,
    speed: int = 46,
    include_header: bool = True,
    include_footer: bool = True,
    show_name: str = "Burlesque",
    captioner_info: str = "Stevie B Bradford Sep 26",
    font_size: str = "LGE"
) -> pd.DataFrame:
    rows = []

    if include_header:
        rows.extend(get_header_rows(show_name, captioner_info, font_size, bright, speed))

    raw_lines = raw_text.splitlines()
    current_speaker = None
    consecutive_blanks = 0

    for raw_line in raw_lines:
        stripped = raw_line.strip()

        if not stripped:
            consecutive_blanks += 1
            if consecutive_blanks == 2:
                rows.extend(make_blanks(3, "Left", bright, speed))
            continue
        else:
            consecutive_blanks = 0

        if stripped.upper() in ("INTERVAL", "[INTERVAL]", "--- INTERVAL ---", "INTERMISSION", "END OF ACT 1", "END OF ACT I"):
            rows.extend(get_interval_rows(bright, speed))
            current_speaker = None
            continue

        if stripped.startswith("******"):
            rows.append(make_row("Left", stripped, bright, speed))
            continue
        pg_match = PAGE_MARKER_REGEX.match(stripped)
        if pg_match:
            p_num = pg_match.group(1)
            p_tot = pg_match.group(2)
            marker = f"******p{p_num}/{p_tot}" if p_tot else f"******p{p_num}"
            rows.append(make_row("Left", marker, bright, speed))
            continue

        if stripped.upper().startswith("CO:"):
            note_body = stripped[3:].strip()
            rows.append(make_row("Left", f"CO:  {note_body}", bright, speed))
            continue

        if (stripped.startswith("[") and stripped.endswith("]")) or (stripped.startswith("(") and stripped.endswith(")")):
            inner = stripped[1:-1].strip().upper()
            if inner.startswith("^") or inner.startswith("♪"):
                inner = "^  " + inner.lstrip("^♪").strip()
            formatted_cue = f"[  {inner}  ]"
            rows.append(make_row("Left", formatted_cue, bright, speed))
            continue

        if stripped.startswith("^") or stripped.startswith("♪"):
            cue_body = stripped.lstrip("^♪").strip()
            if cue_body.isupper() and len(cue_body) < 28 and ":" not in cue_body:
                rows.append(make_row("Centre", f"^  {cue_body}", bright, speed))
            else:
                wrapped = smart_wrap_stg(format_punctuation(cue_body), max_chars, first_line_prefix="^  ")
                for w_line in wrapped:
                    rows.append(make_row("Left", w_line, bright, speed))
            continue

        if stripped.startswith("-"):
            interj_body = format_punctuation(stripped[1:].strip())
            wrapped = smart_wrap_stg(interj_body, max_chars, first_line_prefix=" - ")
            for w_line in wrapped:
                rows.append(make_row("Left", w_line, bright, speed))
            continue

        sp_match = SPEAKER_REGEX.match(stripped)
        if sp_match:
            plus_prefix = "+ " if sp_match.group(1) else ""
            speaker_raw = sp_match.group(2).strip().upper()
            speaker_clean = re.sub(r'\s*/\s*', ' / ', speaker_raw)
            inline_dir = sp_match.group(3)
            speech = sp_match.group(4).strip()

            current_speaker = speaker_clean
            prefix = f"{plus_prefix}{speaker_clean}:  "

            if inline_dir:
                prefix += f"[ {inline_dir.strip().upper()} ]  "

            if not speech:
                rows.append(make_row("Left", f"{plus_prefix}{speaker_clean}:", bright, speed))
                continue

            has_start_caret = False
            if speech.startswith("^") or speech.startswith("♪"):
                has_start_caret = True
                speech = speech.lstrip("^♪").strip()

            has_end_caret = False
            if speech.endswith("^") or speech.endswith("♪"):
                has_end_caret = True
                speech = speech.rstrip("^♪").strip()

            speech_formatted = format_punctuation(speech)
            if has_start_caret:
                prefix += "^  "

            wrapped = smart_wrap_stg(speech_formatted, max_chars, first_line_prefix=prefix)
            if has_end_caret and wrapped:
                wrapped[-1] = f"{wrapped[-1]}  ^"

            for w_line in wrapped:
                rows.append(make_row("Left", w_line, bright, speed))
            continue

        if stripped.isupper() and 2 <= len(stripped) <= 25 and not any(c in stripped for c in ".!?,;\"'"):
            current_speaker = re.sub(r'\s*/\s*', ' / ', stripped)
            continue

        has_start_caret = False
        if stripped.startswith("^") or stripped.startswith("♪"):
            has_start_caret = True
            stripped = stripped.lstrip("^♪").strip()

        has_end_caret = False
        if stripped.endswith("^") or stripped.endswith("♪"):
            has_end_caret = True
            stripped = stripped.rstrip("^♪").strip()

        speech_formatted = format_punctuation(stripped)
        prefix = ""
        if current_speaker:
            prefix = f"{current_speaker}:  "
            current_speaker = None
        if has_start_caret:
            prefix += "^  "

        wrapped = smart_wrap_stg(speech_formatted, max_chars, first_line_prefix=prefix)
        if has_end_caret and wrapped:
            wrapped[-1] = f"{wrapped[-1]}  ^"

        for w_line in wrapped:
            rows.append(make_row("Left", w_line, bright, speed))

    if include_footer:
        rows.extend(get_footer_rows(bright, speed))

    df = pd.DataFrame(rows)
    df.insert(0, "Line", range(1, len(df) + 1))
    return df


def export_stg_string(df: pd.DataFrame) -> str:
    output = io.StringIO()
    output.write("Line\tJustification\tBright\tSpeed\tCaption\n")
    for idx, row in df.iterrows():
        line_num = idx + 1
        just = row["Justification"]
        bright = row["Bright"]
        speed = row["Speed"]
        cap = str(row["Caption"]) if pd.notna(row["Caption"]) else ""
        output.write(f"{line_num}\t{just}\t{bright}\t{speed}\t{cap}\n")
    return output.getvalue()


def extract_text_from_pdf(uploaded_file) -> str:
    pages_text = []
    if HAS_PDFPLUMBER:
        with pdfplumber.open(uploaded_file) as pdf:
            total_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages, start=1):
                pages_text.append(f"******p{i}/{total_pages}")
                txt = page.extract_text(layout=False)
                if txt:
                    pages_text.append(txt)
        return "\n".join(pages_text)
    elif HAS_PYPDF:
        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)
        for i, page in enumerate(reader.pages, start=1):
            pages_text.append(f"******p{i}/{total_pages}")
            txt = page.extract_text()
            if txt:
                pages_text.append(txt)
        return "\n".join(pages_text)
    else:
        return "ERROR: Neither pdfplumber nor pypdf is installed."


# ==========================================
# STREAMLIT UI
# ==========================================

st.set_page_config(
    page_title="StageCap .stg Studio",
    page_icon="🎭",
    layout="wide"
)

st.markdown("""
<style>
    .led-box {
        background-color: #0d0d0d;
        border: 4px solid #333333;
        border-radius: 6px;
        padding: 18px 24px;
        font-family: 'Courier New', Courier, monospace;
        color: #ff9900;
        font-size: 22px;
        font-weight: bold;
        line-height: 1.45;
        letter-spacing: 0.5px;
        box-shadow: inset 0 0 12px #000000, 0 4px 10px rgba(0,0,0,0.4);
        min-height: 125px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .led-line-left {
        text-align: left;
        white-space: pre;
    }
    .led-line-centre {
        text-align: center;
        white-space: pre;
    }
    .co-preview {
        background-color: #1e293b;
        color: #38bdf8;
        font-family: monospace;
        padding: 6px 12px;
        border-radius: 4px;
        margin-top: 8px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎭 StageCap `.stg` Script Converter & Editor")
st.caption("Convert PDF rehearsal scripts or pasted text into Stagetext / DisplayLED `.stg` captioning files.")

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ Hardware & Show Settings")
    show_name = st.text_input("Show Title", value="Burlesque")
    captioner_info = st.text_input("Captioner / Venue / Date Tag", value="Stevie B Bradford Sep 26")
    font_size = st.selectbox("LED Font Size (`CO: FONT SIZE`)", ["LGE", "MED", "SML"], index=0)
    
    col_b, col_s = st.columns(2)
    with col_b:
        bright_val = st.number_input("Brightness", min_value=1, max_value=99, value=46)
    with col_s:
        speed_val = st.number_input("Speed", min_value=1, max_value=99, value=46)
        
    max_chars = st.slider(
        "Max Characters per Line",
        min_value=30,
        max_value=45,
        value=38,
        help="Standard Stagetext LGE font fits 37–39 characters per line."
    )
    
    st.divider()
    st.subheader("📑 Boilerplate Blocks")
    include_header = st.checkbox("Include Stagetext Pre-Show Header", value=True)
    include_footer = st.checkbox("Include Emergency & Evacuation Footer", value=True)

DEFAULT_SAMPLE = """^ LONG HELD NOTE

BOOM!
^ CRASHING CHORDS

SEAN: Ladies and gentlemen, theys and thems. It all starts with a snap...
[ CLICK ]
and the lights start to dim. So, sit back and relax. We'll take care of the rest. Because inside all of us is a little Burlesque...
TROUPE: ...esque... esque... esque...
SEAN: ^ Are you ready for the glitz
CO: choose
The glamour, fashion and powder?
Are you ready for the dolls?
Living for applause
All we need's a couple hours
[ ^ HORNS BLAST ]
SEAN / TROUPE: Louder, louder

INTERVAL

ALI: ^ It's a cold and crazy world
That's raging outside
But baby, me and all my girls are bringing on the fire ^"""

tab_input, tab_editor, tab_simulator = st.tabs([
    "📥 1. Script Input (PDF / Text)",
    "🛠️ 2. Cue Sheet Editor & Validation",
    "📟 3. Live DisplayLED Simulator"
])

with tab_input:
    input_mode = st.radio("Choose Input Source:", ["Paste / Edit Text", "Upload PDF Script"], horizontal=True)
    
    if "raw_script_text" not in st.session_state:
        st.session_state.raw_script_text = DEFAULT_SAMPLE

    if input_mode == "Upload PDF Script":
        uploaded_pdf = st.file_uploader("Upload Rehearsal Script (.pdf)", type=["pdf"])
        if uploaded_pdf is not None:
            if st.button("Extract Text from PDF", type="primary"):
                with st.spinner("Extracting script pages..."):
                    extracted = extract_text_from_pdf(uploaded_pdf)
                    st.session_state.raw_script_text = extracted
                    st.success("PDF extracted! Review or refine the raw text below before converting.")
                    
    raw_input = st.text_area(
        "Raw Script Text (you can edit or paste directly here):",
        value=st.session_state.raw_script_text,
        height=380
    )
    st.session_state.raw_script_text = raw_input

    if st.button("⚡ Convert to .STG Cue Sheet", type="primary", use_container_width=True):
        st.session_state.stg_df = parse_script_to_stg(
            raw_text=st.session_state.raw_script_text,
            max_chars=max_chars,
            bright=bright_val,
            speed=speed_val,
            include_header=include_header,
            include_footer=include_footer,
            show_name=show_name,
            captioner_info=captioner_info,
            font_size=font_size
        )
        st.success(f"Generated {len(st.session_state.stg_df)} `.stg` lines! Switch to the **Cue Sheet Editor** or **Live Simulator** tab.")

if "stg_df" not in st.session_state:
    st.session_state.stg_df = parse_script_to_stg(
        raw_text=st.session_state.raw_script_text,
        max_chars=max_chars,
        bright=bright_val,
        speed=speed_val,
        include_header=include_header,
        include_footer=include_footer,
        show_name=show_name,
        captioner_info=captioner_info,
        font_size=font_size
    )

with tab_editor:
    df = st.session_state.stg_df.copy()
    df["Char_Len"] = df["Caption"].fillna("").astype(str).apply(len)
    over_limit = df[(df["Char_Len"] > max_chars) & (~df["Caption"].str.startswith("CO:", na=False))]

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Total Cue Lines", f"{len(df):,}")
    col_m2.metric("Dialogue / Lyric Lines", f"{len(df[df['Caption'].str.strip() != '']):,}")
    col_m3.metric("Operator Notes (CO:)", f"{len(df[df['Caption'].str.startswith('CO:', na=False)]):,}")
    col_m4.metric(f"Lines > {max_chars} chars", f"{len(over_limit)}", delta_color="inverse" if len(over_limit) > 0 else "off")

    edited_df = st.data_editor(
        df[["Line", "Justification", "Bright", "Speed", "Caption", "Char_Len"]],
        column_config={
            "Line": st.column_config.NumberColumn("Line", disabled=True, width="small"),
            "Justification": st.column_config.SelectboxColumn("Justification", options=["Left", "Centre", "Right"], width="small"),
            "Bright": st.column_config.NumberColumn("Bright", min_value=1, max_value=99, width="small"),
            "Speed": st.column_config.NumberColumn("Speed", min_value=1, max_value=99, width="small"),
            "Caption": st.column_config.TextColumn("Caption", width="large"),
            "Char_Len": st.column_config.NumberColumn("Chars", disabled=True, width="small"),
        },
        num_rows="dynamic",
        use_container_width=True,
        height=480,
        hide_index=True
    )

    edited_df["Line"] = range(1, len(edited_df) + 1)
    st.session_state.stg_df = edited_df[["Line", "Justification", "Bright", "Speed", "Caption"]]

    stg_content = export_stg_string(st.session_state.stg_df)
    safe_filename = f"{show_name.replace(' ', '-')}-{captioner_info.replace(' ', '-')}"

    dl_col1, dl_col2 = st.columns(2)
    with dl_col1:
        st.download_button(
            label="💾 Download .stg File",
            data=stg_content,
            file_name=f"{safe_filename}.stg",
            mime="text/plain",
            type="primary",
            use_container_width=True
        )
    with dl_col2:
        st.download_button(
            label="📄 Download .stg.txt File",
            data=stg_content,
            file_name=f"{safe_filename}.stg.txt",
            mime="text/plain",
            use_container_width=True
        )

with tab_simulator:
    st.subheader("📟 3-Line DisplayLED Unit Simulator")
    sim_df = st.session_state.stg_df

    if "sim_line_idx" not in st.session_state:
        st.session_state.sim_line_idx = 14

    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 3])
    with nav_col1:
        if st.button("⬅️ Previous Cue", use_container_width=True):
            st.session_state.sim_line_idx = max(1, st.session_state.sim_line_idx - 1)
    with nav_col2:
        if st.button("Next Cue ➡️", type="primary", use_container_width=True):
            st.session_state.sim_line_idx = min(len(sim_df), st.session_state.sim_line_idx + 1)
    with nav_col3:
        selected_line = st.slider(
            "Scrub through show cues:",
            min_value=1,
            max_value=max(1, len(sim_df)),
            value=min(st.session_state.sim_line_idx, len(sim_df))
        )
        st.session_state.sim_line_idx = selected_line

    subset = sim_df.iloc[:st.session_state.sim_line_idx]
    visible_rows = subset[~subset["Caption"].fillna("").str.startswith("CO:")].tail(3)
    
    current_row = sim_df.iloc[st.session_state.sim_line_idx - 1]
    current_cap = str(current_row["Caption"]) if pd.notna(current_row["Caption"]) else ""

    led_html_lines = []
    for _, r in visible_rows.iterrows():
        cap_text = str(r["Caption"]) if pd.notna(r["Caption"]) else ""
        display_text = cap_text.replace("^", "♪") if cap_text else "&nbsp;"
        align_class = "led-line-centre" if r["Justification"] == "Centre" else "led-line-left"
        led_html_lines.append(f'<div class="{align_class}">{display_text}</div>')

    while len(led_html_lines) < 3:
        led_html_lines.insert(0, '<div class="led-line-left">&nbsp;</div>')

    st.markdown(f'<div class="led-box">{"".join(led_html_lines)}</div>', unsafe_allow_html=True)

    if current_cap.startswith("CO:"):
        st.markdown(f'<div class="co-preview">🔒 <b>OPERATOR SCREEN ONLY (Not sent to LED):</b> {current_cap}</div>', unsafe_allow_html=True)

    st.markdown("##### Upcoming Queue Window")
    window_start = max(0, st.session_state.sim_line_idx - 3)
    window_end = min(len(sim_df), st.session_state.sim_line_idx + 8)
    queue_slice = sim_df.iloc[window_start:window_end].copy()
    queue_slice["Active"] = ["👉 CURRENT" if i == st.session_state.sim_line_idx else "" for i in queue_slice["Line"]]
    st.dataframe(queue_slice[["Active", "Line", "Justification", "Caption"]], use_container_width=True, hide_index=True)
