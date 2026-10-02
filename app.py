import pickle
from pathlib import Path

import numpy as np
import streamlit as st

# ---------------------------------------------------------------- setup ----
st.set_page_config(page_title="Tramy | Next Word", page_icon="✍️", layout="centered")

BASE = Path(__file__).parent
CREAM, DARK, ORANGE = "#F0E7D9", "#1B150F", "#FA601F"
SUGGESTIONS = 5
STYLES = {"Focused": 0.0, "Balanced": 0.7, "Adventurous": 1.2}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Poppins:wght@400;500;600&display=swap');

/* hide Streamlit chrome */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], .stDeployButton { display: none !important; }
header[data-testid="stHeader"] { background: transparent; height: 0; }

.stApp { background: {CREAM}; }
html, body, .stApp, .stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button {
    font-family: 'Poppins', sans-serif;
}
.block-container { max-width: 760px; padding-top: 3rem; padding-bottom: 4rem; }

/* header */
.hero-title {
    font-family: 'Playfair Display', serif; font-weight: 700;
    font-size: 3rem; line-height: 1.1; color: {DARK}; margin: 0 0 .5rem 0;
}
.hero-sub { color: {DARK}; opacity: .72; font-size: 1.05rem; margin: 0 0 2rem 0; max-width: 34rem; }
.hero-rule { width: 56px; height: 5px; background: {ORANGE}; border-radius: 999px; margin: 0 0 1.1rem 0; }

/* force a light look even when the browser or OS is in dark mode */
:root, .stApp { color-scheme: light; }

/* labels */
.stTextArea label p, .stNumberInput label p, .stSelectbox label p {
    color: {DARK} !important; font-weight: 500; font-size: .92rem;
}

/* text area */
.stTextArea div[data-baseweb="textarea"],
.stTextArea div[data-baseweb="base-input"],
.stTextArea textarea {
    background: #FBF7F0 !important; background-color: #FBF7F0 !important;
}
.stTextArea div[data-baseweb="textarea"] {
    border: 1.5px solid {DARK} !important; border-radius: 16px !important;
}
.stTextArea div[data-baseweb="textarea"]:focus-within {
    border-color: {ORANGE} !important; box-shadow: 0 0 0 3px rgba(250, 96, 31, .25) !important;
}
.stTextArea textarea {
    color: {DARK} !important; -webkit-text-fill-color: {DARK} !important; caret-color: {ORANGE};
    font-size: 1.15rem; line-height: 1.6; padding: 1rem 1.1rem;
}
.stTextArea textarea::placeholder { color: {DARK} !important; -webkit-text-fill-color: {DARK} !important; opacity: .45; }

/* number input */
.stNumberInput div[data-baseweb="input"],
.stNumberInput div[data-baseweb="base-input"],
.stNumberInput input {
    background: #FBF7F0 !important; background-color: #FBF7F0 !important;
    color: {DARK} !important; -webkit-text-fill-color: {DARK} !important;
}
.stNumberInput div[data-baseweb="input"] {
    border: 1.5px solid {DARK} !important; border-radius: 12px !important; overflow: hidden;
}
.stNumberInput div[data-baseweb="input"]:focus-within { border-color: {ORANGE} !important; }
.stNumberInput button { background: #FBF7F0 !important; color: {DARK} !important; border: none !important; }
.stNumberInput button:hover { background: rgba(250, 96, 31, .18) !important; }
.stNumberInput button svg { fill: {DARK} !important; color: {DARK} !important; }

/* select box */
.stSelectbox div[data-baseweb="select"] > div {
    background: #FBF7F0 !important; background-color: #FBF7F0 !important;
    border: 1.5px solid {DARK} !important; border-radius: 12px !important;
}
.stSelectbox div[data-baseweb="select"] > div:focus-within { border-color: {ORANGE} !important; }
.stSelectbox div[data-baseweb="select"] * {
    color: {DARK} !important; -webkit-text-fill-color: {DARK} !important;
}
.stSelectbox svg { fill: {DARK} !important; }

/* dropdown list (rendered outside the app, so it needs its own rules) */
div[data-baseweb="popover"], div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] ul, div[data-baseweb="menu"] {
    background: #FBF7F0 !important; background-color: #FBF7F0 !important;
}
div[data-baseweb="popover"] li, div[data-baseweb="popover"] li * {
    background: #FBF7F0 !important; color: {DARK} !important; -webkit-text-fill-color: {DARK} !important;
}
div[data-baseweb="popover"] li:hover, div[data-baseweb="popover"] li[aria-selected="true"] {
    background: rgba(250, 96, 31, .2) !important;
}

/* buttons (general) */
.stButton > button {
    background: transparent; color: {DARK}; border: 1.5px solid {DARK};
    border-radius: 999px; padding: .55rem 1.4rem; font-weight: 500; transition: all .15s ease;
}
.stButton > button p { color: inherit; font-weight: 500; }
.stButton > button:hover { background: {DARK}; color: {CREAM}; border-color: {DARK}; }
.stButton > button:focus-visible { outline: 3px solid rgba(250, 96, 31, .5); outline-offset: 2px; }
.stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"] {
    background: {ORANGE}; color: {DARK}; border-color: {ORANGE}; font-weight: 600;
}
.stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: {DARK}; color: {ORANGE}; border-color: {DARK};
}

/* results panel */
.st-key-results {
    background: {DARK}; border-radius: 22px; padding: 1.6rem 1.7rem 1.4rem 1.7rem; margin-top: 1.6rem;
}
.panel-title {
    font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 600;
    color: {CREAM}; margin-bottom: .2rem;
}
.panel-note { color: {CREAM}; opacity: .62; font-size: .92rem; margin-bottom: 1rem; }
.st-key-results .stButton > button {
    color: {CREAM}; border-color: rgba(240, 231, 217, .55); width: 100%;
    font-size: 1.05rem; padding: .5rem 1rem;
}
.st-key-results .stButton > button:hover { background: {ORANGE}; color: {DARK}; border-color: {ORANGE}; }
.meter { display: flex; align-items: center; gap: .8rem; }
.meter .track { flex: 1; height: 10px; border-radius: 999px; background: rgba(240, 231, 217, .14); overflow: hidden; }
.meter .fill { height: 100%; border-radius: 999px; background: {ORANGE}; }
.meter span { color: {CREAM}; font-size: .9rem; min-width: 3.4rem; text-align: right; opacity: .9; }

@media (max-width: 640px) {
    .hero-title { font-size: 2.3rem; }
    .st-key-results { padding: 1.2rem; }
}
</style>
"""
for token, value in {"{CREAM}": CREAM, "{DARK}": DARK, "{ORANGE}": ORANGE}.items():
    CSS = CSS.replace(token, value)
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------- model ----
@st.cache_resource(show_spinner="Loading the model...")
def load_assets():
    from tensorflow.keras.models import load_model

    model = load_model(BASE / "lstm_model.h5", compile=False)
    with open(BASE / "tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
    max_len = None
    try:
        with open(BASE / "max_len.pkl", "rb") as f:
            max_len = int(pickle.load(f))
    except Exception:
        pass  # optional: the model itself tells us the input length

    # The model's own input width is the safest source of truth.
    try:
        seq_len = int(model.input_shape[1])
    except Exception:
        if max_len is None:
            raise RuntimeError("Could not work out the input length. Add max_len.pkl next to app.py.")
        seq_len = max_len - 1
    index_word = {i: w for w, i in tokenizer.word_index.items()}
    return model, tokenizer, seq_len, index_word


def predict_probs(text, model, tokenizer, seq_len):
    ids = tokenizer.texts_to_sequences([text])[0]
    if not ids:
        return None
    ids = ids[-seq_len:]
    padded = np.zeros((1, seq_len), dtype="int32")
    padded[0, -len(ids):] = ids
    probs = model.predict(padded, verbose=0)[0].astype("float64")
    probs[0] = 0.0  # padding index is never a real word
    return probs


def choose(probs, temperature):
    if temperature <= 0:
        return int(probs.argmax())
    p = np.log(probs + 1e-9) / temperature
    p = np.exp(p - p.max())
    p[0] = 0.0
    p /= p.sum()
    return int(np.random.choice(len(p), p=p))


# ------------------------------------------------------------ callbacks ----
if "text" not in st.session_state:
    st.session_state.text = ""


def add_word(word):
    st.session_state.text = f"{st.session_state.text.rstrip()} {word}".strip()


def clear_text():
    st.session_state.text = ""


def continue_writing():
    try:
        model, tokenizer, seq_len, index_word = load_assets()
    except Exception:
        return
    text = st.session_state.text.strip()
    temperature = STYLES[st.session_state.style]
    for _ in range(int(st.session_state.n_words)):
        probs = predict_probs(text, model, tokenizer, seq_len)
        if probs is None:
            break
        word = index_word.get(choose(probs, temperature))
        if not word:
            break
        text = f"{text} {word}"
    st.session_state.text = text


# ------------------------------------------------------------------- UI ----
st.markdown(
    """
    <div class="hero-rule"></div>
    <div class="hero-title">What comes next?</div>
    <div class="hero-sub">Type a few words and the model suggests the word that should follow.
    Tap a suggestion to add it.</div>
    """,
    unsafe_allow_html=True,
)

st.text_area(
    "Your text",
    key="text",
    height=130,
    placeholder="Start writing here...",
)

c1, c2, c3 = st.columns([1, 1, 1.4], vertical_alignment="bottom")
c1.number_input("Words to add", min_value=1, max_value=50, value=10, step=1, key="n_words")
c2.selectbox("Style", list(STYLES.keys()), index=1, key="style")
with c3:
    a, b = st.columns(2)
    a.button("Continue", type="primary", on_click=continue_writing, use_container_width=True)
    b.button("Clear", on_click=clear_text, use_container_width=True)

# --------------------------------------------------------------- results ----
try:
    model, tokenizer, seq_len, index_word = load_assets()
    ready = True
except Exception as exc:
    ready = False
    load_error = str(exc)

with st.container(key="results"):
    st.markdown('<div class="panel-title">Likely next words</div>', unsafe_allow_html=True)

    if not ready:
        st.markdown(
            '<div class="panel-note">The model could not be loaded. Check that lstm_model.h5, '
            "tokenizer.pkl and max_len.pkl are in the same folder as this app, and that "
            "TensorFlow is installed.</div>",
            unsafe_allow_html=True,
        )
        st.caption(load_error[:300])
    elif not st.session_state.text.strip():
        st.markdown(
            '<div class="panel-note">Suggestions will appear here once you start typing.</div>',
            unsafe_allow_html=True,
        )
    else:
        probs = predict_probs(st.session_state.text, model, tokenizer, seq_len)
        if probs is None:
            st.markdown(
                '<div class="panel-note">The model does not know any of these words yet. '
                "Try different words.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="panel-note">Bar length shows how confident the model is.</div>',
                unsafe_allow_html=True,
            )
            top = [i for i in np.argsort(probs)[::-1] if i in index_word][:SUGGESTIONS]
            peak = max(probs[top[0]], 1e-9)
            for rank, idx in enumerate(top):
                left, right = st.columns([2, 3], vertical_alignment="center")
                left.button(
                    index_word[idx],
                    key=f"suggestion_{rank}",
                    on_click=add_word,
                    args=(index_word[idx],),
                    use_container_width=True,
                )
                width = max(probs[idx] / peak * 100, 2)
                right.markdown(
                    f'<div class="meter"><div class="track"><div class="fill" '
                    f'style="width:{width:.1f}%"></div></div>'
                    f"<span>{probs[idx] * 100:.1f}%</span></div>",
                    unsafe_allow_html=True,
                )