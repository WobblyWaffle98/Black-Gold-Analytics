import os
import re
import html
from datetime import datetime, timedelta

import nltk
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from curl_cffi import requests
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from plotly.subplots import make_subplots
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from sklearn.feature_extraction.text import CountVectorizer

# ---------------------------------------------------------------- page setup
# set_page_config must be the first Streamlit command
ICON = os.path.join("Images", "Black_Gold_Icon.png")
st.set_page_config(
    page_title="Black Gold Analytics",
    page_icon=ICON if os.path.exists(ICON) else "🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

GOLD, GREEN, RED, GREY = "#F2C14E", "#34D399", "#F87171", "#6B6B6B"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&family=Inter:wght@400;500;600&display=swap');
:root{--gold:#F2C14E;--gold2:#FFD978;--line:rgba(255,255,255,.09);--mute:#8E8B84;--panel:#0C0C0D;
--grad:linear-gradient(135deg,#FFE08A,#F2B632 45%,#B8801A)}
html,body,.stApp{background:#000!important;color:#F4F1E8;font-family:Inter,sans-serif}
.main .block-container{max-width:1500px;padding:1.5rem 2.5rem 3rem}
#MainMenu,footer,.stDeployButton{visibility:hidden}
header[data-testid="stHeader"]{background:transparent}
[data-testid="stSidebar"]{background:#0A0A0B;border-right:1px solid var(--line)}
[data-testid="stSidebar"] h2{font-family:Sora,sans-serif;font-size:1.1rem}

/* brand + hero */
.brand{font:700 clamp(2rem,4.5vw,3.2rem) Sora,sans-serif;letter-spacing:-.02em;padding:.4rem 0 .2rem}
.brand::before{content:"";display:inline-block;width:.5em;height:.5em;margin-right:.4em;border-radius:50% 0 50% 50%;
transform:rotate(-45deg);background:var(--grad)}
.brand span{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.hl{font:700 clamp(2rem,4vw,3.4rem)/1.05 Sora,sans-serif;letter-spacing:-.03em;margin-top:2.2rem}
.hero-sub{color:var(--mute);font-size:1rem;margin:.9rem 0 0;max-width:52ch}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);border:1px solid var(--line);
border-radius:16px;overflow:hidden;margin-top:2.2rem}
.stat{background:var(--panel);padding:1.3rem}
.stat b{display:block;font:700 2.1rem/1.1 Sora,sans-serif;background:var(--grad);-webkit-background-clip:text;
background-clip:text;color:transparent}
.stat span{color:var(--mute);font-size:.82rem}
.stat em{font-style:normal;font-size:.8rem;margin-left:.4rem}

/* section titles */
.sec{font:600 1.5rem Sora,sans-serif;letter-spacing:-.02em;margin:2.6rem 0 .2rem}
.sec-sub{color:var(--mute);font-size:.88rem;margin-bottom:1rem}

/* bordered containers become cards */
[data-testid="stVerticalBlockBorderWrapper"]{background:var(--panel);border:1px solid var(--line)!important;border-radius:16px}
.week-date{color:var(--gold2);font-size:.85rem;margin-top:1rem}

/* widgets */
.stButton>button,.stDownloadButton>button{border-radius:999px;border:1px solid var(--gold);background:transparent;
color:var(--gold2);font-weight:600}
.stButton>button:hover,.stDownloadButton>button:hover{background:var(--gold);color:#000;border-color:var(--gold)}
.stButton>button[kind="primary"]{background:var(--grad);color:#000;border:0}
div[role="radiogroup"]{gap:.4rem}
div[role="radiogroup"]>label{background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:999px;padding:.25rem .9rem}
div[role="radiogroup"]>label:has(input:checked){background:var(--grad);color:#000;border-color:transparent}
div[role="radiogroup"]>label>div:first-child{display:none}
span[data-baseweb="tag"]{background:rgba(242,193,78,.14)!important;color:var(--gold2)!important;border-radius:999px}
.stTextInput input{border-radius:999px!important;background:rgba(255,255,255,.04)!important;border:1px solid var(--line)!important;
padding:.7rem 1.1rem!important}
.stTextInput input:focus{border-color:var(--gold)!important}

/* status, chips, feed */
.status{display:inline-block;padding:.25rem .8rem;border-radius:999px;font-size:.8rem;border:1px solid var(--line)}
.status.ok{color:#34D399;background:rgba(52,211,153,.1)}
.status.bad{color:#F87171;background:rgba(248,113,113,.1)}
.chip{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:.1rem .65rem;margin:.15rem .2rem 0 0;
font-size:.78rem;color:var(--mute)}
.ring-t{font-weight:600;margin-bottom:.2rem}
.feed{background:var(--panel);border:1px solid var(--line);border-radius:16px;overflow:hidden}
.news{display:grid;grid-template-columns:84px 1fr auto;gap:1rem;padding:1.05rem 1.4rem;border-top:1px solid var(--line);
border-left:3px solid #6B6B6B}
.news:first-child{border-top:0}
.news:hover{background:rgba(242,193,78,.04)}
.news.s-bullish{border-left-color:#34D399}.news.s-bearish{border-left-color:#F87171}
.n-date{color:var(--mute);font-size:.82rem}
.n-title{font-weight:600;line-height:1.35}
.n-why{color:var(--mute);font-size:.86rem;margin-top:.2rem}
.n-meta{text-align:right;white-space:nowrap}
.pill{display:inline-block;padding:.1rem .7rem;border-radius:999px;font-size:.74rem;font-weight:600}
.pill.s-bullish{background:rgba(52,211,153,.14);color:#34D399}
.pill.s-bearish{background:rgba(248,113,113,.14);color:#F87171}
.pill.s-neutral{background:rgba(255,255,255,.07);color:var(--mute)}
.n-cat{display:block;color:var(--mute);font-size:.78rem;margin-top:.3rem}
.read{display:inline-block;color:var(--gold2)!important;font-size:.8rem;margin-top:.2rem;text-decoration:none}
.read:hover{text-decoration:underline}
.foot{text-align:center;color:var(--mute);font-size:.8rem;padding:2.5rem 0 0}
@media (max-width:768px){.news{grid-template-columns:1fr}.n-meta{text-align:left}.stats{grid-template-columns:1fr}
.main .block-container{padding:1rem}}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------- NLP setup
@st.cache_resource
def setup_nlp():
    for pkg in ("wordnet", "omw-1.4", "stopwords"):
        try:
            nltk.download(pkg, quiet=True)
        except Exception:
            pass
    custom = {
        'oil', 'sentiment', 'prices', 'market', 'bullish', 'suggests', 'could', 'will', 'may', 'can',
        'would', 'should', 'might', 'com', 'crude', 'today', 'oilprice', 'bloomberg', 'reuters', 'price',
        'wsj', 'say', 'wall', 'street', 'journal', 'wall street',
    }
    try:
        stops = set(stopwords.words('english')).union(custom)
    except Exception:
        stops = custom
    return WordNetLemmatizer(), stops


lemmatizer, stop_words = setup_nlp()


def preprocess(text):
    try:
        tokens = re.findall(r'\b[a-z]+\b', str(text).lower())
        return ' '.join(lemmatizer.lemmatize(t) for t in tokens if t not in stop_words and len(t) > 2)
    except Exception:
        return str(text).lower()


def get_top_phrases(text_series, top_n=5, ngram_range=(1, 2)):
    try:
        cleaned = text_series.dropna().astype(str).apply(preprocess)
        if len(cleaned) == 0:
            return []
        vec = CountVectorizer(stop_words=list(stop_words), ngram_range=ngram_range)
        X = vec.fit_transform(cleaned)
        sums = X.sum(axis=0)
        freq = [(w, int(sums[0, i])) for w, i in vec.vocabulary_.items()]
        return sorted(freq, key=lambda x: x[1], reverse=True)[:top_n]
    except Exception:
        return []

# ---------------------------------------------------------------- data access
uri = st.secrets.db_credentials.url


@st.cache_resource
def get_client():
    return MongoClient(uri, server_api=ServerApi('1'))


@st.cache_data(ttl=300)
def load_weekly_summaries():
    try:
        coll = get_client()['blackgold_db']['Weekly_News']
        summaries = list(coll.find({}, sort=[("Date", -1)]))
        if summaries:
            return {'summaries': summaries, 'success': True}
        return {'summaries': [], 'success': False, 'error': 'No weekly summaries found'}
    except Exception as e:
        return {'summaries': [], 'success': False, 'error': str(e)}


@st.cache_data(ttl=600)
def load_data(collection_name):
    try:
        db = get_client()['blackgold_db']
        coll = db['rss_articles'] if collection_name == "Groq Analysis" else db['rss_articles_gemini']
        data = list(coll.find({}))
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        if 'Sentiment V2' in df.columns:
            df['Sentiment'] = df['Sentiment V2']
        elif 'Sentiment' not in df.columns:
            df['Sentiment'] = 'neutral'
        if 'Category' not in df.columns:
            df['Category'] = 'General'
        if 'Reasoning' not in df.columns:
            df['Reasoning'] = 'Analysis pending'
        return df.dropna(subset=['Date'])
    except Exception as e:
        st.error(f"Error loading data from MongoDB: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=900)
def load_brent_data(start_date, end_date):
    try:
        session = requests.Session(impersonate="chrome")
        brent = yf.download('BZ=F', start=start_date, end=end_date + timedelta(days=1),
                            session=session, progress=False)
        if brent.empty:
            return pd.DataFrame()
        if isinstance(brent.columns, pd.MultiIndex):
            brent.columns = brent.columns.get_level_values(0)
        brent = brent.reset_index()
        brent['Date'] = pd.to_datetime(brent['Date'])
        return brent
    except Exception as e:
        print("Brent error:", e)
        return pd.DataFrame()


def to_dt(value):
    if isinstance(value, str):
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except Exception:
            return datetime.now()
    return value or datetime.now()


def format_weekly_summary(content):
    if not content:
        return ""
    keys = ['overview', 'macroeconomic', 'supply', 'demand', 'key events', 'market implications']
    out = []
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        if ':' in line and len(line) < 100:
            out.append(f"### {line}" if any(k in line.lower() for k in keys) else f"**{line}**")
        else:
            out.append(line)
    return '\n\n'.join(out)


def prepare_csv(df):
    if df.empty:
        return pd.DataFrame()
    out = df.copy()
    out = out.drop(columns=['_id'], errors='ignore')
    out['Date'] = out['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    first = [c for c in ['Date', 'Title', 'Category', 'Sentiment', 'Reasoning', 'Link'] if c in out.columns]
    return out[first + [c for c in out.columns if c not in first]]

# ---------------------------------------------------------------- charts
def style_fig(fig, height=None):
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color="#B9B6AE"),
        margin=dict(t=20, b=30, l=10, r=10), height=height,
        legend=dict(orientation="h", y=1.1, x=0),
    )
    fig.update_xaxes(gridcolor='rgba(255,255,255,.06)', zeroline=False)
    fig.update_yaxes(gridcolor='rgba(255,255,255,.06)', zeroline=False)
    return fig


def net_score(series):
    return int((series == 'bullish').sum() - (series == 'bearish').sum())


def donut(sentiments):
    fig = go.Figure()
    if len(sentiments):
        counts = sentiments.value_counts()
        colors = {'bullish': GREEN, 'bearish': RED, 'neutral': GREY}
        fig.add_trace(go.Pie(
            labels=counts.index.tolist(), values=counts.tolist(), hole=0.74, sort=False,
            marker=dict(colors=[colors.get(k, GOLD) for k in counts.index], line=dict(color='#0C0C0D', width=3)),
            textinfo='none', hovertemplate='%{label}: %{value} (%{percent})<extra></extra>', showlegend=False))
        net = net_score(sentiments)
        fig.add_annotation(text=f"<b>{net:+d}</b>", showarrow=False,
                           font=dict(size=26, color=GREEN if net >= 0 else RED, family="Sora, sans-serif"))
    else:
        fig.add_annotation(text="No data", showarrow=False, font=dict(size=14, color="#8E8B84"))
    return style_fig(fig, height=190).update_layout(margin=dict(t=5, b=5, l=5, r=5))


def combined_chart(df, brent, mode):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    has_brent = not brent.empty
    if mode != "Brent" and len(df):
        score = df['Sentiment'].map({'bullish': 1, 'bearish': -1}).fillna(0)
        net = score.groupby(df['Date'].dt.normalize()).sum()
        fig.add_bar(x=net.index, y=net.values, name="Net sentiment", opacity=.8,
                    marker_color=[GREEN if v >= 0 else RED for v in net.values], secondary_y=False)
    if mode != "Sentiment" and has_brent:
        fig.add_scatter(x=brent['Date'], y=brent['Close'], mode='lines', name="Brent close (USD)",
                        line=dict(color=GOLD, width=2.4), secondary_y=True)
    if mode != "Sentiment" and not has_brent:
        fig.add_annotation(text="Connection to Yahoo Finance failed. Please try again later.",
                           xref="paper", yref="paper", x=.5, y=.5, showarrow=False, font=dict(color=RED))
    style_fig(fig, height=380)
    fig.update_yaxes(title_text="Net sentiment (bullish minus bearish)", secondary_y=False,
                     visible=mode != "Brent")
    fig.update_yaxes(title_text="Brent close (USD)", secondary_y=True, showgrid=False,
                     visible=mode != "Sentiment")
    fig.update_layout(hovermode="x unified")
    return fig

# ---------------------------------------------------------------- header
if 'wk' not in st.session_state:
    st.session_state.wk = 0
if 'feed_n' not in st.session_state:
    st.session_state.feed_n = 25

st.markdown('<div class="brand">Black Gold <span>Analytics</span></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Analysis model")
    collection_choice = st.radio(
        "Analysis model", ["Gemini Analysis", "Groq Analysis"], label_visibility="collapsed",
        help="Gemini is the default, a more complex model for sentiment analysis. Groq is a backup that "
             "gives another perspective on market sentiment.")
    st.markdown("---")

hero_slot = st.container()  # filled once the data and filters are known

# ---------------------------------------------------------------- weekly summary
st.markdown('<div class="sec">Weekly market summary</div>'
            '<div class="sec-sub">Written each week from the full news flow.</div>', unsafe_allow_html=True)

weekly = load_weekly_summaries()
if weekly['success'] and weekly['summaries']:
    summaries = weekly['summaries']
    total = len(summaries)
    st.session_state.wk = min(st.session_state.wk, total - 1)

    def step(delta):
        st.session_state.wk = max(0, min(total - 1, st.session_state.wk + delta))

    labels = [f"Week of {to_dt(s.get('Date')).strftime('%B %d, %Y')}" for s in summaries]
    n1, n2, n3 = st.columns([1, 1, 4])
    n1.button("Older week", on_click=step, args=(1,), use_container_width=True, disabled=st.session_state.wk >= total - 1)
    n2.button("Newer week", on_click=step, args=(-1,), use_container_width=True, disabled=st.session_state.wk <= 0)
    chosen = n3.selectbox("Jump to week", labels, index=st.session_state.wk, label_visibility="collapsed")
    st.session_state.wk = labels.index(chosen)

    current = summaries[st.session_state.wk]
    body = format_weekly_summary(current.get('WeeklyNews', ''))
    with st.container(border=True):
        if body:
            st.markdown(body)
            st.markdown(f'<div class="week-date">{labels[st.session_state.wk]} · {st.session_state.wk + 1} of {total}</div>',
                        unsafe_allow_html=True)
        else:
            st.caption("Weekly summary content is being processed.")
elif weekly['success']:
    st.info("No weekly summaries available yet.")
else:
    st.error(f"Unable to load weekly summaries: {weekly.get('error', 'Unknown error')}")

# ---------------------------------------------------------------- load articles
with st.spinner(f"Loading data from {collection_choice}..."):
    df = load_data(collection_choice)

if df.empty:
    st.markdown('<span class="status bad">No data available or connection failed</span>', unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------------- sidebar filters
with st.sidebar:
    st.markdown("## Filters")
    if st.button("Refresh data", type="primary", use_container_width=True):
        load_data.clear()
        load_brent_data.clear()
        load_weekly_summaries.clear()
        st.rerun()
    st.markdown("---")

    min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
    default_start = max(min_date, max_date - timedelta(days=90))
    start_date = st.date_input("Start date", value=default_start, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)
    if start_date > end_date:
        st.error("Start date must be before end date.")
        st.stop()

    st.markdown("---")
    categories = sorted(df['Category'].dropna().unique())
    selected_categories = st.multiselect("Categories", categories, default=categories)
    only_bb = st.checkbox("Show only bullish and bearish sentiment", value=True)

# ---------------------------------------------------------------- filtering
start_dt = pd.to_datetime(start_date)
end_dt = pd.to_datetime(end_date) + timedelta(days=1) - timedelta(seconds=1)
df_filtered = df[(df['Date'] >= start_dt) & (df['Date'] <= end_dt)]
if selected_categories:
    df_filtered = df_filtered[df_filtered['Category'].isin(selected_categories)]
if only_bb:
    df_filtered = df_filtered[df_filtered['Sentiment'].isin(['bullish', 'bearish'])]

# Windows count back from the end of the selected range (not from today), so they
# still show data when the newest articles are a few days old.
df_3d = df_filtered[df_filtered['Date'] > end_dt - timedelta(days=3)]
df_7d = df_filtered[df_filtered['Date'] > end_dt - timedelta(days=7)]
df_30d = df_filtered[df_filtered['Date'] > end_dt - timedelta(days=30)]

brent_data = load_brent_data(start_date, end_date)

with st.sidebar:
    st.markdown("---")
    csv_df = prepare_csv(df_filtered)
    if not csv_df.empty:
        st.download_button(
            f"Download CSV ({len(csv_df)} records)", data=csv_df.to_csv(index=False),
            file_name=f"blackgold_sentiment_{start_date:%Y%m%d}_to_{end_date:%Y%m%d}.csv",
            mime="text/csv", use_container_width=True)
        st.caption(f"Date range: {start_date} to {end_date}")
    else:
        st.caption("No data available for download with current filters.")

# ---------------------------------------------------------------- hero
if not brent_data.empty and 'Close' in brent_data.columns:
    closes = brent_data['Close'].dropna()
    last_close = f"{closes.iloc[-1]:.2f}"
    delta = closes.iloc[-1] - closes.iloc[-2] if len(closes) > 1 else 0
    brent_delta = f'<em style="color:{GREEN if delta >= 0 else RED}">{delta:+.2f}</em>'
else:
    last_close, brent_delta = "n/a", ""

with hero_slot:
    st.markdown(
        '<div class="stats">'
        f'<div class="stat"><b>{last_close}{brent_delta}</b><span>Brent close, USD</span></div>'
        f'<div class="stat"><b>{net_score(df_7d["Sentiment"]):+d}</b><span>Net sentiment, 7 days</span></div>'
        f'<div class="stat"><b>{len(df_filtered)}</b><span>Headlines in range</span></div>'
        '</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------- sentiment overview
st.markdown('<div class="sec">Sentiment overview</div>'
            '<div class="sec-sub"><span class="status ok">Connected to MongoDB</span></div>', unsafe_allow_html=True)

cols = st.columns(4)
for col, (data, period) in zip(cols, [(df_filtered, "Selected range"), (df_3d, "Last 3 days"),
                                      (df_7d, "Last 7 days"), (df_30d, "Last 30 days")]):
    with col:
        with st.container(border=True):
            st.markdown(f'<div class="ring-t">{period}</div>', unsafe_allow_html=True)
            st.plotly_chart(donut(data['Sentiment']), use_container_width=True,
                            config={'displayModeBar': False}, key=f"donut_{period}")
            st.caption(f"{len(data)} headlines")
            if len(data):
                phrases = get_top_phrases(data['Title'])
                st.markdown(''.join(f'<span class="chip">{html.escape(w)} ({c})</span>' for w, c in phrases),
                            unsafe_allow_html=True)

# ---------------------------------------------------------------- charts
st.markdown('<div class="sec">Net sentiment against Brent</div>'
            '<div class="sec-sub">Daily bullish minus bearish headlines, set over the front-month Brent close.</div>',
            unsafe_allow_html=True)
mode = st.radio("Chart view", ["Combined", "Sentiment", "Brent"], horizontal=True, label_visibility="collapsed")
with st.container(border=True):
    if len(df_filtered) == 0 and mode != "Brent":
        st.caption("No data available for the selected filters to display the trend chart.")
    else:
        st.plotly_chart(combined_chart(df_filtered, brent_data, mode), use_container_width=True,
                        config={'displayModeBar': False})

# ---------------------------------------------------------------- news feed
st.markdown('<div class="sec">News feed</div>', unsafe_allow_html=True)
query = st.text_input("Search news articles", placeholder="Search titles, categories or analysis",
                      label_visibility="collapsed")

feed_df = df_filtered.sort_values('Date', ascending=False)
if query:
    q = query.lower()
    mask = (feed_df['Title'].astype(str).str.lower().str.contains(q, regex=False, na=False)
            | feed_df['Category'].astype(str).str.lower().str.contains(q, regex=False, na=False)
            | feed_df['Reasoning'].astype(str).str.lower().str.contains(q, regex=False, na=False))
    feed_df = feed_df[mask]
st.markdown(f'<div class="sec-sub">{len(feed_df)} headlines in range'
            f'{" matching “" + html.escape(query) + "”" if query else ""}</div>', unsafe_allow_html=True)

if feed_df.empty:
    st.info("No articles found for these filters. Widen the date range or add categories.")
else:
    cards = []
    for _, row in feed_df.head(st.session_state.feed_n).iterrows():
        sent = str(row['Sentiment']).lower()
        cls = f"s-{sent}" if sent in ('bullish', 'bearish') else "s-neutral"
        link = row.get('Link')
        read = (f'<a class="read" href="{html.escape(str(link))}" target="_blank">Read article</a>'
                if pd.notna(link) and link else "")
        cards.append(
            f'<div class="news {cls}"><div class="n-date">{row["Date"]:%d %b %Y}</div>'
            f'<div><div class="n-title">{html.escape(str(row["Title"]))}</div>'
            f'<div class="n-why">{html.escape(str(row.get("Reasoning", "Analysis not available")))}</div></div>'
            f'<div class="n-meta"><span class="pill {cls}">{sent.title()}</span>'
            f'<span class="n-cat">{html.escape(str(row.get("Category", "General")))}</span>{read}</div></div>')
    st.markdown(f'<div class="feed">{"".join(cards)}</div>', unsafe_allow_html=True)
    if len(feed_df) > st.session_state.feed_n:
        if st.button("Show more"):
            st.session_state.feed_n += 25
            st.rerun()

st.markdown('<div class="foot">© 2026 Black Gold Analytics · Premium Market Intelligence</div>', unsafe_allow_html=True)
