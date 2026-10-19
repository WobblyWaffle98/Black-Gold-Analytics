import os
import re
import html
from datetime import date, datetime, timedelta

import nltk
import numpy as np
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
.alert{border:1px solid var(--gold);background:rgba(242,193,78,.08);border-radius:12px;padding:.7rem 1rem;margin:.6rem 0;
color:var(--gold2);font-size:.9rem}
.alert.up{border-color:#34D399;background:rgba(52,211,153,.08);color:#34D399}
.alert.dn{border-color:#F87171;background:rgba(248,113,113,.08);color:#F87171}
.chip-score{display:inline-block;border-radius:999px;padding:.2rem .9rem;font-weight:700;font-size:.9rem}
.takes{margin:.5rem 0 1rem 1.1rem;padding:0}.takes li{margin:.35rem 0;line-height:1.5}
.kpi{font:700 2rem/1.1 Sora,sans-serif;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.kpi-l{color:var(--mute);font-size:.82rem;margin-top:.2rem}
.kpi-s{color:var(--mute);font-size:.8rem;margin-top:.4rem}
.dis{border-top:1px solid var(--line);padding:1rem 1.4rem}
.dis:first-child{border-top:0}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line);
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
def load_data():
    try:
        db = get_client()['blackgold_db']
        coll = db['rss_articles_gemini']
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
        df = df.dropna(subset=['Date']).copy()
        if df['Date'].dt.tz is not None:
            df['Date'] = df['Date'].dt.tz_localize(None)
        df['Sentiment'] = df['Sentiment'].astype(str).str.lower()
        df = df.sort_values('Date').reset_index(drop=True)
        df['Story'] = cluster_stories(df['Title'], df['Date'])
        df['Sources'] = df.groupby('Story')['Story'].transform('size')
        return df
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
SCORE = {'bullish': 1, 'bearish': -1}


def cluster_stories(titles, dates, threshold=0.6, window_days=2):
    """Group near-identical headlines (one story, many outlets) by word overlap within a few days.
    Expects rows sorted by date."""
    reps, ids = [], []
    for title, dt in zip(titles.astype(str), dates):
        toks = set(preprocess(title).split())
        found = None
        for i in range(len(reps) - 1, -1, -1):
            rt, rd = reps[i]
            if (dt - rd).days > window_days:
                break
            if toks and rt and len(toks & rt) / len(toks | rt) >= threshold:
                found = i
                break
        if found is None:
            reps.append((toks, dt))
            found = len(reps) - 1
        ids.append(found)
    return ids


def story_view(df, dedupe):
    return df.drop_duplicates('Story') if dedupe else df


def outlets(row):
    n = int(row.get('Sources', 1) or 1)
    return f'<span class="n-cat">Covered by {n} outlets</span>' if n > 1 else ''


def trading_day_scores(df, idx):
    """Net and total headline counts per Brent trading day. Weekend news rolls into the next trading day."""
    s = df['Sentiment'].map(SCORE).fillna(0).values
    pos = idx.searchsorted(df['Date'].dt.normalize().values)
    ok = pos < len(idx)
    g = pd.DataFrame({'td': idx[pos[ok]], 'net': s[ok], 'n': 1}).groupby('td').sum()
    return g.reindex(idx).fillna(0)


def build_signal(df, brent):
    """Normalised sentiment (net / total headlines), its 7-day average and z-score, aligned to Brent
    trading days, plus forward returns."""
    px = brent.set_index('Date')['Close'].dropna().sort_index()
    px.index = px.index.normalize()
    px = px[~px.index.duplicated()]
    g = trading_day_scores(df, px.index)
    n7 = g['n'].rolling(7, min_periods=3).sum().replace(0, np.nan)
    roll = g['net'].rolling(7, min_periods=3).sum() / n7
    sig = pd.DataFrame({
        'px': px, 'daily': g['net'] / g['n'].replace(0, np.nan), 'roll': roll,
        'z': (roll - roll.mean()) / roll.std(), 'ret1d': px.pct_change()})
    for h in (1, 5, 20):
        sig[f'fwd{h}'] = px.shift(-h) / px - 1
    return sig


def horizon_stats(sig, basis, h):
    d = sig[[basis, f'fwd{h}']].dropna()
    d = d[d[basis] != 0]
    if len(d) < 20:
        return None
    ret = d[f'fwd{h}']
    return dict(n=len(d), corr=d[basis].corr(ret), hit=(np.sign(d[basis]) == np.sign(ret)).mean(),
                bull=ret[d[basis] > 0].mean(), bear=ret[d[basis] < 0].mean())


def lead_lag(sig, max_lag=10):
    rows = []
    for k in range(-max_lag, max_lag + 1):
        pair = pd.concat([sig['daily'], sig['ret1d'].shift(-k)], axis=1).dropna()
        rows.append((k, pair.iloc[:, 0].corr(pair.iloc[:, 1]) if len(pair) > 20 else np.nan, len(pair)))
    return pd.DataFrame(rows, columns=['lag', 'corr', 'n'])


def regime(v, band=0.05):
    return 'bullish' if v > band else 'bearish' if v < -band else 'neutral'


def alert_messages(sig, thr):
    msgs = []
    roll, z = sig['roll'].dropna(), sig['z'].dropna()
    if z.empty:
        return msgs
    if abs(z.iloc[-1]) >= thr:
        msgs.append(('up' if z.iloc[-1] > 0 else 'dn',
                     f"7-day sentiment z-score is {z.iloc[-1]:+.2f}, beyond the ±{thr:.1f} threshold."))
    if len(roll) > 5 and regime(roll.iloc[-1]) != regime(roll.iloc[-6]):
        msgs.append(('up' if roll.iloc[-1] > roll.iloc[-6] else 'dn',
                     f"Regime change: {regime(roll.iloc[-6])} to {regime(roll.iloc[-1])} over the last 5 trading days."))
    return msgs


def category_drivers(df, end_dt):
    s = df.assign(score=df['Sentiment'].map(SCORE).fillna(0))
    this = s[(s['Date'] > end_dt - timedelta(days=7)) & (s['Date'] <= end_dt)]
    prev = s[(s['Date'] > end_dt - timedelta(days=14)) & (s['Date'] <= end_dt - timedelta(days=7))]
    out = pd.concat([this.groupby('Category')['score'].sum().rename('this'),
                     prev.groupby('Category')['score'].sum().rename('prev')], axis=1).fillna(0)
    out['change'] = out['this'] - out['prev']
    return out.sort_values('this')


def top_events(df, px, n=10):
    """The most widely covered stories, placed on the Brent price line."""
    ev = (df.sort_values(['Sources', 'Date'], ascending=False).drop_duplicates('Story').head(n)
          .sort_values('Date').reset_index(drop=True))
    ev['y'] = px.reindex(pd.DatetimeIndex(ev['Date'].dt.normalize()), method='bfill').values
    return ev.dropna(subset=['y'])


def event_card(row):
    s = str(row['Sentiment']).lower()
    cls = f"s-{s}" if s in ('bullish', 'bearish') else "s-neutral"
    link = row.get('Link')
    a = f'<a class="read" href="{html.escape(str(link))}" target="_blank">Read article</a>' if pd.notna(link) and link else ''
    return (f'<div class="feed"><div class="news {cls}"><div class="n-date">{row["Date"]:%d %b %Y}</div>'
            f'<div><div class="n-title">{html.escape(str(row["Title"]))}</div>'
            f'<div class="n-why">{html.escape(str(row.get("Reasoning", "")))}</div></div>'
            f'<div class="n-meta"><span class="pill {cls}">{s.title()}</span>{outlets(row)}{a}</div></div></div>')


KEY_TERMS = ('opec', 'supply', 'demand', 'inventor', 'stock', 'china', 'fed', 'rate', 'sanction', 'output',
             'cut', 'forecast', 'tariff', 'refin', 'export', 'import', 'recession', 'dollar', 'geopolit')


def takeaways(text, n=4):
    """Pick the n most informative sentences from the weekly summary (extractive, no AI call)."""
    clean = re.sub(r'[#*_`>]', ' ', text or '')
    sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean) if 40 <= len(s.strip()) <= 240]
    score = lambda s: sum(t in s.lower() for t in KEY_TERMS) + len(re.findall(r'\d', s)) / 6
    top = sorted(range(len(sents)), key=lambda i: score(sents[i]), reverse=True)[:n]
    return [sents[i] for i in sorted(top)]


def build_digest(sig, drv, df, last_close, alerts):
    lines = [f"Black Gold Analytics digest, {datetime.now():%d %b %Y}", f"Brent close: {last_close}"]
    if sig is not None and sig['roll'].notna().any():
        r = sig['roll'].dropna().iloc[-1]
        zt = f", z-score {sig['z'].dropna().iloc[-1]:+.2f}" if sig['z'].notna().any() else ""
        lines.append(f"7-day sentiment score: {r:+.2f} ({regime(r)}){zt}")
    lines += [f"ALERT: {m}" for _, m in alerts]
    if len(drv):
        top = drv.reindex(drv['change'].abs().sort_values(ascending=False).index).head(3)
        lines.append("Biggest category moves (net, week on week): " +
                     "; ".join(f"{c} {v.this:+.0f} ({v.change:+.0f})" for c, v in top.iterrows()))
    heads = df.sort_values(['Sources', 'Date'], ascending=False).drop_duplicates('Story').head(3)
    lines += ["Top headlines:"] + [f"- {r.Title} [{str(r.Sentiment).title()}]" for r in heads.itertuples()]
    return "\n".join(lines)


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


def combined_chart(df, brent, mode, events=None):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    has_brent = not brent.empty
    if mode != "Brent" and len(df):
        score = df['Sentiment'].map(SCORE).fillna(0)
        grp = score.groupby(df['Date'].dt.normalize())
        daily = grp.mean()
        full = pd.date_range(daily.index.min(), daily.index.max())
        roll = (grp.sum().reindex(full, fill_value=0).rolling(7, min_periods=1).sum()
                / grp.size().reindex(full, fill_value=0).rolling(7, min_periods=1).sum().replace(0, np.nan))
        fig.add_bar(x=daily.index, y=daily.values, name="Daily score", opacity=.55,
                    marker_color=[GREEN if v >= 0 else RED for v in daily.values], secondary_y=False)
        fig.add_scatter(x=roll.index, y=roll.values, mode='lines', name="7-day average",
                        line=dict(color="#F4F1E8", width=2, dash='dot'), secondary_y=False)
    if mode != "Sentiment" and has_brent:
        fig.add_scatter(x=brent['Date'], y=brent['Close'], mode='lines', name="Brent close (USD)",
                        line=dict(color=GOLD, width=2.4), secondary_y=True)
    if events is not None and len(events) and mode != "Sentiment" and has_brent:
        fig.add_scatter(
            x=events['Date'], y=events['y'], mode='markers', name='Key headlines',
            customdata=events.index.tolist(), text=events['Title'].str.slice(0, 90),
            marker=dict(size=13, line=dict(color=GOLD, width=2),
                        color=[GREEN if s == 'bullish' else RED if s == 'bearish' else GREY
                               for s in events['Sentiment']]),
            hovertemplate='%{x|%d %b}<br>%{text}<extra>Key headline</extra>', secondary_y=True)
    if mode != "Sentiment" and not has_brent:
        fig.add_annotation(text="Connection to Yahoo Finance failed. Please try again later.",
                           xref="paper", yref="paper", x=.5, y=.5, showarrow=False, font=dict(color=RED))
    style_fig(fig, height=380)
    fig.update_yaxes(title_text="Sentiment score (-1 to +1)", range=[-1, 1], secondary_y=False,
                     visible=mode != "Brent")
    fig.update_yaxes(title_text="Brent close (USD)", secondary_y=True, showgrid=False,
                     visible=mode != "Sentiment")
    fig.update_layout(hovermode="x unified")
    return fig

# ---------------------------------------------------------------- header
qp = st.query_params


def _iso(v):
    try:
        return date.fromisoformat(v)
    except Exception:
        return None


def _float(v, default):
    try:
        return float(v)
    except Exception:
        return default


defaults = {
    'wk': 0, 'feed_n': 25,
    'rng': qp.get('range') if qp.get('range') in ('7D', '30D', '90D', 'All', 'Custom') else '90D',
    'only_bb': qp.get('bb', '1') == '1',
    'dedupe': qp.get('dedupe', '1') == '1',
    'cmp': qp.get('cmp', '0') == '1',
    'thr': _float(qp.get('thr'), 1.0),
}
for _k, _v in defaults.items():
    st.session_state.setdefault(_k, _v)
if _iso(qp.get('start')) and _iso(qp.get('end')):
    st.session_state.setdefault('c_start', _iso(qp.get('start')))
    st.session_state.setdefault('c_end', _iso(qp.get('end')))

st.markdown('<div class="brand">Black Gold <span>Analytics</span></div>', unsafe_allow_html=True)

hero_slot = st.container()  # filled once the data and filters are known
alert_slot = st.container()

with st.spinner("Loading data..."):
    df = load_data()

if df.empty:
    st.markdown('<span class="status bad">No data available or connection failed</span>', unsafe_allow_html=True)
    st.stop()

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
            # Score covers the 7 days ending on the summary's date. If your summaries are dated at the
            # start of the week, change this window to start at the anchor instead.
            anchor = pd.Timestamp(to_dt(current.get('Date')))
            anchor = (anchor.tz_localize(None) if anchor.tzinfo else anchor).normalize()
            wdf = story_view(df, st.session_state.dedupe)
            wdf = wdf[(wdf['Date'] >= anchor - timedelta(days=6)) & (wdf['Date'] < anchor + timedelta(days=1))]
            tips = takeaways(current.get('WeeklyNews', ''))
            if len(wdf):
                ws = wdf['Sentiment'].map(SCORE).fillna(0).mean()
                wc = GREEN if ws > 0.05 else RED if ws < -0.05 else GREY
                st.markdown(f'<span class="chip-score" style="background:{wc}22;color:{wc}">Week score {ws:+.2f}</span>'
                            f'<span class="n-cat" style="display:inline;margin-left:.7rem">{len(wdf)} headlines</span>',
                            unsafe_allow_html=True)
            if tips:
                st.markdown('<div class="ring-t" style="margin-top:.9rem">Key takeaways</div><ul class="takes">'
                            + ''.join(f'<li>{html.escape(t)}</li>' for t in tips) + '</ul>', unsafe_allow_html=True)
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
pass  # articles are loaded above the weekly summary

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
    st.radio("Range", ["7D", "30D", "90D", "All", "Custom"], key="rng", horizontal=True)
    if st.session_state.rng == "Custom":
        st.session_state.setdefault('c_start', max(min_date, max_date - timedelta(days=29)))
        st.session_state.setdefault('c_end', max_date)
        st.session_state.c_start = min(max(st.session_state.c_start, min_date), max_date)
        st.session_state.c_end = min(max(st.session_state.c_end, min_date), max_date)
        start_date = st.date_input("Start date", key="c_start", min_value=min_date, max_value=max_date)
        end_date = st.date_input("End date", key="c_end", min_value=min_date, max_value=max_date)
    else:
        span = {"7D": 7, "30D": 30, "90D": 90}.get(st.session_state.rng)
        end_date = max_date
        start_date = max(min_date, max_date - timedelta(days=span - 1)) if span else min_date
    if start_date > end_date:
        st.error("Start date must be before end date.")
        st.stop()
    st.checkbox("Compare with previous period", key="cmp")

    st.markdown("---")
    categories = sorted(df['Category'].dropna().unique())
    if 'cats' not in st.session_state:
        st.session_state.cats = [c for c in qp.get('cats', '').split(',') if c in categories] or categories
    else:
        valid = [c for c in st.session_state.cats if c in categories]
        if len(valid) != len(st.session_state.cats):
            st.session_state.cats = valid or categories
    selected_categories = st.multiselect("Categories", categories, key="cats")
    only_bb = st.checkbox("Show only bullish and bearish sentiment", key="only_bb")
    st.checkbox("Count each story once", key="dedupe",
                help="Merges near-identical headlines from different outlets so one event counts once.")

    st.markdown("---")
    st.markdown("## Alerts")
    thr = st.number_input("Alert when the 7-day z-score passes ±", min_value=0.5, max_value=3.0, step=0.1, key="thr")

# ---------------------------------------------------------------- filtering
start_dt = pd.to_datetime(start_date)
end_dt = pd.to_datetime(end_date) + timedelta(days=1) - timedelta(seconds=1)


def apply_filters(d, a, b):
    d = d[(d['Date'] >= a) & (d['Date'] <= b)]
    if selected_categories:
        d = d[d['Category'].isin(selected_categories)]
    if only_bb:
        d = d[d['Sentiment'].isin(['bullish', 'bearish'])]
    return d


df_u = story_view(df, st.session_state.dedupe)
df_filtered = apply_filters(df_u, start_dt, end_dt)
prev_end = start_dt - timedelta(seconds=1)
df_prev = apply_filters(df_u, prev_end - (end_dt - start_dt), prev_end)

# Windows count back from the end of the selected range (not from today), so they
# still show data when the newest articles are a few days old.
df_3d = df_filtered[df_filtered['Date'] > end_dt - timedelta(days=3)]
df_7d = df_filtered[df_filtered['Date'] > end_dt - timedelta(days=7)]
df_30d = df_filtered[df_filtered['Date'] > end_dt - timedelta(days=30)]

brent_data = load_brent_data(start_date, end_date)

# Signal, alerts and the predictive panel use the full article history (not only the selected range)
brent_full = load_brent_data(min_date, datetime.now().date())
df_sig = df_u[df_u['Category'].isin(selected_categories)] if selected_categories else df_u
sig = build_signal(df_sig, brent_full) if (not brent_full.empty and 'Close' in brent_full.columns) else None
alerts = alert_messages(sig, thr) if sig is not None else []
with alert_slot:
    for kind, msg in alerts:
        st.markdown(f'<div class="alert {kind}">{html.escape(msg)}</div>', unsafe_allow_html=True)

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
    st.caption("Filters are saved in the page URL. Copy the address to share this view.")

# ---------------------------------------------------------------- hero
if not brent_data.empty and 'Close' in brent_data.columns:
    closes = brent_data['Close'].dropna()
    last_close = f"{closes.iloc[-1]:.2f}"
    delta = closes.iloc[-1] - closes.iloc[-2] if len(closes) > 1 else 0
    brent_delta = f'<em style="color:{GREEN if delta >= 0 else RED}">{delta:+.2f}</em>'
else:
    last_close, brent_delta = "n/a", ""

score_txt = z_txt = "n/a"
if sig is not None and sig['roll'].notna().any():
    score_txt = f"{sig['roll'].dropna().iloc[-1]:+.2f}"
    if sig['z'].notna().any():
        z_txt = f"{sig['z'].dropna().iloc[-1]:+.1f}σ"

with hero_slot:
    st.markdown(
        '<div class="stats">'
        f'<div class="stat"><b>{last_close}{brent_delta}</b><span>Brent close, USD</span></div>'
        f'<div class="stat"><b>{score_txt}</b><span>Sentiment score, 7-day average (-1 to +1)</span></div>'
        f'<div class="stat"><b>{z_txt}</b><span>Score vs its own history</span></div>'
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
            sc = data['Sentiment'].map(SCORE).fillna(0).mean() if len(data) else 0.0
            line = f"{len(data)} headlines · score {sc:+.2f}"
            if period == "Selected range" and st.session_state.cmp:
                ps = df_prev['Sentiment'].map(SCORE).fillna(0).mean() if len(df_prev) else 0.0
                line += f" · previous period {ps:+.2f} ({sc - ps:+.2f})"
            st.caption(line)
            if len(data):
                phrases = get_top_phrases(data['Title'])
                st.markdown(''.join(f'<span class="chip">{html.escape(w)} ({c})</span>' for w, c in phrases),
                            unsafe_allow_html=True)

# ---------------------------------------------------------------- charts
st.markdown('<div class="sec">Net sentiment against Brent</div>'
            '<div class="sec-sub">Daily score (bullish minus bearish, divided by headlines) with its 7-day average, '
            'over the front-month Brent close. Dots mark the most widely covered stories: click one to read it.</div>',
            unsafe_allow_html=True)
mode = st.radio("Chart view", ["Combined", "Sentiment", "Brent"], horizontal=True, label_visibility="collapsed")
events = None
if not brent_data.empty and 'Close' in brent_data.columns and len(df_filtered):
    px_sel = brent_data.set_index('Date')['Close'].dropna().sort_index()
    px_sel.index = px_sel.index.normalize()
    events = top_events(df_filtered, px_sel[~px_sel.index.duplicated()])

picked = None
with st.container(border=True):
    if len(df_filtered) == 0 and mode != "Brent":
        st.caption("No data available for the selected filters to display the trend chart.")
    else:
        chart_fig = combined_chart(df_filtered, brent_data, mode, events)
        try:
            chart_sel = st.plotly_chart(chart_fig, use_container_width=True, config={'displayModeBar': False},
                                        on_select="rerun", selection_mode="points", key="main_chart")
        except TypeError:  # older Streamlit without chart selection
            st.plotly_chart(chart_fig, use_container_width=True, config={'displayModeBar': False})
            chart_sel = None
        if chart_sel and events is not None:
            for pt in chart_sel.get("selection", {}).get("points", []):
                cd = pt.get("customdata")
                cd = cd[0] if isinstance(cd, (list, tuple)) and cd else cd
                if isinstance(cd, (int, np.integer)) and cd in events.index:
                    picked = events.loc[cd]
                    break
if picked is not None:
    st.markdown(event_card(picked), unsafe_allow_html=True)

# ---------------------------------------------------------------- news feed
# ---- does sentiment predict price?
st.markdown('<div class="sec">Does sentiment predict price?</div>'
            '<div class="sec-sub">Sentiment score against Brent returns over the following 1, 5 and 20 trading days, '
            'using the full article history rather than the selected range. Neutral headlines count in the total.</div>',
            unsafe_allow_html=True)
if sig is None or sig['roll'].notna().sum() < 30:
    st.info("Not enough overlapping sentiment and Brent history yet to test this.")
else:
    basis_label = st.radio("Signal", ["7-day average score", "Daily score"], horizontal=True,
                           label_visibility="collapsed")
    basis = 'roll' if basis_label.startswith("7") else 'daily'
    for col, h in zip(st.columns(3), (1, 5, 20)):
        stt = horizon_stats(sig, basis, h)
        with col, st.container(border=True):
            if stt is None:
                st.caption(f"{h}-day horizon: not enough data")
            else:
                st.markdown(
                    f'<div class="kpi">{stt["corr"]:+.2f}</div>'
                    f'<div class="kpi-l">Correlation with the next {h} trading day{"s" if h > 1 else ""}</div>'
                    f'<div class="kpi-s">Hit rate {stt["hit"]:.0%} over {stt["n"]} days</div>'
                    f'<div class="kpi-s">Average return after bullish days {stt["bull"]:+.2%}, '
                    f'after bearish days {stt["bear"]:+.2%}</div>', unsafe_allow_html=True)
    ll = lead_lag(sig)
    band = 1.96 / np.sqrt(max(float(ll['n'].median()), 1))
    lead = ll[(ll['lag'] >= 1) & (ll['lag'] <= 5)].dropna()
    ll_fig = go.Figure(go.Bar(x=ll['lag'], y=ll['corr'], marker_color=[GOLD if k > 0 else GREY for k in ll['lag']],
                              hovertemplate='Lag %{x} days: %{y:.3f}<extra></extra>'))
    for y in (band, -band):
        ll_fig.add_hline(y=y, line_dash="dot", line_color="#8E8B84")
    style_fig(ll_fig, height=300).update_layout(
        xaxis_title="Days (positive: sentiment leads price, negative: sentiment follows price)",
        yaxis_title="Correlation with daily return")
    with st.container(border=True):
        st.plotly_chart(ll_fig, use_container_width=True, config={'displayModeBar': False})
        if len(lead) and lead['corr'].abs().max() > band:
            best = lead.loc[lead['corr'].abs().idxmax()]
            st.caption(f"Sentiment shows a link to returns {int(best['lag'])} day(s) later "
                       f"(correlation {best['corr']:+.2f}, noise level ±{band:.2f}).")
        else:
            st.caption(f"No lead beyond noise: gold bars stay inside the dotted ±{band:.2f} lines.")
        st.caption("Gold bars compare today's score with the return k days later. Grey bars show price moves that came "
                   "before the sentiment. The 5 and 20-day figures use overlapping windows, so treat them as indicative.")

# ---- category drivers
st.markdown('<div class="sec">What is driving sentiment</div>'
            '<div class="sec-sub">Net bullish minus bearish headlines by category: the last 7 days of the range '
            'against the 7 days before.</div>', unsafe_allow_html=True)
drv = category_drivers(df_filtered, end_dt) if len(df_filtered) else pd.DataFrame(columns=['this', 'prev', 'change'])
if drv.empty:
    st.caption("No category data for the selected filters.")
else:
    drv_fig = go.Figure()
    drv_fig.add_bar(y=drv.index, x=drv['prev'], name="Previous 7 days", orientation='h', marker_color=GREY)
    drv_fig.add_bar(y=drv.index, x=drv['this'], name="Last 7 days", orientation='h', marker_color=GOLD)
    style_fig(drv_fig, height=max(260, 46 * len(drv) + 90)).update_layout(barmode='group')
    mover = drv['change'].abs().idxmax()
    with st.container(border=True):
        st.plotly_chart(drv_fig, use_container_width=True, config={'displayModeBar': False})
        st.caption(f"Biggest change: {mover}, from {drv.loc[mover, 'prev']:+.0f} to {drv.loc[mover, 'this']:+.0f} net.")

# ---- digest
with st.expander("Daily digest and notifications"):
    digest = build_digest(sig, drv, df_filtered, last_close, alerts)
    st.code(digest, language=None)
    d1, d2 = st.columns(2)
    d1.download_button("Download digest", digest, file_name=f"blackgold_digest_{datetime.now():%Y%m%d}.txt",
                       mime="text/plain", use_container_width=True)
    hook = (st.secrets.get("alerts") or {}).get("webhook_url")
    if hook:
        if d2.button("Send to Slack or Teams", use_container_width=True):
            try:
                requests.post(hook, json={"text": digest}, timeout=10)
                st.success("Digest sent.")
            except Exception as e:
                st.error(f"Could not send: {e}")
    else:
        st.caption("Add [alerts] webhook_url to your Streamlit secrets to enable sending. "
                   "Pushing alerts automatically each day needs a scheduled job that runs this logic.")

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
            f'<span class="n-cat">{html.escape(str(row.get("Category", "General")))}</span>'
            f'{outlets(row)}{read}</div></div>')
    st.markdown(f'<div class="feed">{"".join(cards)}</div>', unsafe_allow_html=True)
    if len(feed_df) > st.session_state.feed_n:
        if st.button("Show more"):
            st.session_state.feed_n += 25
            st.rerun()

params = {"range": st.session_state.rng,
          "bb": "1" if only_bb else "0", "dedupe": "1" if st.session_state.dedupe else "0",
          "cmp": "1" if st.session_state.cmp else "0", "thr": f"{thr:.1f}"}
if st.session_state.rng == "Custom":
    params.update(start=start_date.isoformat(), end=end_date.isoformat())
if set(selected_categories) != set(categories):
    params["cats"] = ",".join(selected_categories)
st.query_params.from_dict(params)

st.markdown('<div class="foot">© 2026 Black Gold Analytics · Premium Market Intelligence</div>', unsafe_allow_html=True)
