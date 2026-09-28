import base64
import hmac
import html as html_lib
import io
import json
import os
import zipfile
import re
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, time as dt_time
from zoneinfo import ZoneInfo
from email.message import EmailMessage
from email.utils import formatdate
from urllib.parse import parse_qs, quote, quote_plus, unquote, urljoin, urlparse

import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# DESIGN SYSTEM (theme, CSS & HTML components)
# ==========================================

APP_NAME = "Customer Growth"
APP_TAGLINE = "Keep in touch & grow existing accounts"

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --bg: #0A0E1A;
  --surface: #111827;
  --surface-2: #161F33;
  --surface-3: #1C2740;
  --border: rgba(148, 163, 184, 0.14);
  --border-strong: rgba(148, 163, 184, 0.26);
  --text: #E7EAF3;
  --muted: #8C98B0;
  --faint: #5E6A82;
  --accent: #7C83FF;
  --accent-2: #38D6F5;
  --accent-soft: rgba(124, 131, 255, 0.14);
  --good: #34D399;
  --warn: #FBBF24;
  --risk: #FB923C;
  --bad: #F87171;
  --radius: 14px;
  --grad: linear-gradient(135deg, #7C83FF 0%, #38D6F5 100%);
}

html, body, [class*="css"], .stApp, button, input, textarea, select {
  font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif !important;
}
.stApp {
  background:
    radial-gradient(1200px 500px at 85% -10%, rgba(56, 214, 245, 0.07), transparent 60%),
    radial-gradient(900px 500px at 10% -20%, rgba(124, 131, 255, 0.10), transparent 60%),
    var(--bg);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stDecoration"] { display: none; }
footer { visibility: hidden; }
.block-container { padding-top: 1.6rem !important; padding-bottom: 3rem !important; max-width: 1500px; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0D1322 0%, #0A0E1A 100%);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] .block-container, [data-testid="stSidebarContent"] { padding-top: 0.6rem; }
[data-testid="stSidebarUserContent"] { padding-top: 1rem; }

/* ---------- Typography ---------- */
h1, h2, h3, h4 { color: var(--text); letter-spacing: -0.02em; }
p, li, label, .stMarkdown { color: var(--text); }
[data-testid="stCaptionContainer"], .stCaption { color: var(--muted) !important; }
[data-testid="stWidgetLabel"] p {
  font-size: 0.76rem !important; font-weight: 600 !important; color: var(--muted) !important;
  text-transform: uppercase; letter-spacing: 0.06em;
}

/* ---------- Cards (bordered containers) ---------- */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]),
div[data-testid="stVerticalBlockBorderWrapper"] {
  border-radius: var(--radius) !important;
}
.st-key-card-queue { margin-top: 18px; }
.st-key-card-left, .st-key-card-select, .st-key-card-right, .st-key-card-login, .st-key-card-queue {
  background: linear-gradient(180deg, rgba(22, 31, 51, 0.85) 0%, rgba(17, 24, 39, 0.85) 100%);
  border: 1px solid var(--border) !important;
  border-radius: var(--radius);
  padding: 22px 22px 18px 22px;
  box-shadow: 0 1px 0 rgba(255,255,255,0.03) inset, 0 20px 40px -24px rgba(0,0,0,0.6);
}

/* ---------- Inputs ---------- */
[data-baseweb="input"], [data-baseweb="select"] > div, [data-baseweb="textarea"] {
  background: var(--surface) !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: 10px !important;
  transition: border-color .15s ease, box-shadow .15s ease;
}
[data-baseweb="input"]:focus-within, [data-baseweb="select"] > div:focus-within, [data-baseweb="textarea"]:focus-within {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 3px var(--accent-soft) !important;
}
[data-baseweb="input"] input, [data-baseweb="textarea"] textarea { color: var(--text) !important; }
[data-baseweb="input"] > div, [data-baseweb="base-input"] { background: transparent !important; }
textarea { font-family: 'Inter', sans-serif !important; font-size: 0.9rem !important; line-height: 1.55 !important; }

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
  border-radius: 10px !important; font-weight: 600 !important; padding: 0.55rem 1.1rem !important;
  border: 1px solid var(--border-strong) !important; background: var(--surface-2) !important;
  color: var(--text) !important; transition: all .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {
  border-color: var(--accent) !important; color: #fff !important; transform: translateY(-1px);
}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"], .stFormSubmitButton > button,
[data-testid="stBaseButton-primary"] {
  background: var(--grad) !important; border: none !important; color: #0A0E1A !important;
  box-shadow: 0 8px 24px -10px rgba(124, 131, 255, 0.8);
}
.stButton > button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {
  filter: brightness(1.08); color: #0A0E1A !important;
}
.stButton > button[kind="primary"] p, [data-testid="stBaseButton-primary"] p, .stFormSubmitButton > button p { color: #0A0E1A !important; font-weight: 700 !important; }

.stLinkButton a, [data-testid^="stBaseLinkButton"] {
  border-radius: 10px !important; font-weight: 700 !important; padding: 0.55rem 1.1rem !important;
}
[data-testid="stBaseLinkButton-primary"], .stLinkButton a[kind="primary"] {
  background: var(--grad) !important; border: none !important; color: #0A0E1A !important;
  box-shadow: 0 8px 24px -10px rgba(124, 131, 255, 0.8);
}
[data-testid="stBaseLinkButton-primary"] p, .stLinkButton a[kind="primary"] p { color: #0A0E1A !important; font-weight: 700 !important; }
[data-testid="stBaseLinkButton-primary"]:hover { filter: brightness(1.08); }

/* ---------- Tabs ---------- */
[data-testid="stTabs"] [role="tablist"], [data-baseweb="tab-list"] {
  gap: 4px; background: var(--surface); padding: 4px; border-radius: 12px; border: 1px solid var(--border);
}
[data-testid="stTabs"] [role="tab"], [data-baseweb="tab"] {
  border-radius: 9px !important; padding: 8px 16px !important; height: auto !important;
  color: var(--muted) !important; background: transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"], [data-baseweb="tab"][aria-selected="true"] { background: var(--surface-3) !important; color: var(--text) !important; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"], [data-testid="stTabs"] .react-aria-SelectionIndicator { display: none !important; }
[data-testid="stTabs"] [role="tab"] p { font-weight: 600; font-size: 0.86rem; }
[data-testid="stTabs"] [role="tablist"] { width: fit-content; margin-bottom: 6px; }

/* ---------- Table, expanders, alerts ---------- */
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }
[data-testid="stExpander"] details { background: var(--surface); border: 1px solid var(--border) !important; border-radius: 12px !important; }
[data-testid="stExpander"] summary p { font-size: 0.85rem; color: var(--muted); font-weight: 600; }
[data-testid="stAlert"] { border-radius: 12px !important; border: 1px solid var(--border) !important; }
[data-testid="stCode"] pre, .stCode pre { background: var(--surface) !important; border: 1px solid var(--border); border-radius: 12px; }
hr { border-color: var(--border) !important; }

/* ================= Custom components ================= */
.pe-hero { display: flex; align-items: center; justify-content: space-between; gap: 24px; flex-wrap: wrap;
  padding: 6px 2px 22px 2px; margin-bottom: 18px; border-bottom: 1px solid var(--border); }
.pe-eyebrow { display: inline-flex; align-items: center; gap: 8px; font-size: 0.72rem; font-weight: 700;
  letter-spacing: 0.14em; text-transform: uppercase; color: var(--accent-2); margin-bottom: 8px; }
.pe-eyebrow .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--good); box-shadow: 0 0 0 4px rgba(52,211,153,.15); }
.pe-title { font-size: 2.05rem; font-weight: 800; letter-spacing: -0.035em; line-height: 1.1; margin: 0; color: var(--text); }
.pe-title span { background: var(--grad); -webkit-background-clip: text; background-clip: text; color: transparent; }
.pe-sub { color: var(--muted); font-size: 0.95rem; margin-top: 8px; max-width: 620px; }

.pe-stepper { display: flex; align-items: center; gap: 6px; background: var(--surface); border: 1px solid var(--border);
  border-radius: 999px; padding: 6px; }
.pe-step { display: flex; align-items: center; gap: 8px; padding: 7px 14px 7px 7px; border-radius: 999px;
  font-size: 0.82rem; font-weight: 600; color: var(--faint); white-space: nowrap; }
.pe-step .num { width: 24px; height: 24px; border-radius: 50%; display: grid; place-items: center; font-size: 0.72rem;
  font-weight: 700; border: 1px solid var(--border-strong); color: var(--faint); }
.pe-step.done { color: var(--muted); }
.pe-step.done .num { background: rgba(52,211,153,.14); border-color: rgba(52,211,153,.45); color: var(--good); }
.pe-step.active { background: var(--surface-3); color: var(--text); }
.pe-step.active .num { background: var(--grad); border: none; color: #0A0E1A; }
.pe-step-sep { width: 14px; height: 1px; background: var(--border-strong); }

.pe-section { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
.pe-section .badge { width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center;
  background: var(--accent-soft); color: var(--accent); font-weight: 800; font-size: 0.85rem; border: 1px solid rgba(124,131,255,.3); }
.pe-section .t { font-size: 1.08rem; font-weight: 700; color: var(--text); line-height: 1.2; }
.pe-section .s { font-size: 0.82rem; color: var(--muted); margin-top: 2px; }

.pe-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.pe-chip { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 999px; font-size: 0.76rem;
  font-weight: 600; background: var(--surface-3); color: var(--text); border: 1px solid var(--border); white-space: nowrap; }
.pe-chip.accent { background: var(--accent-soft); color: #B9BDFF; border-color: rgba(124,131,255,.3); }
.pe-chip.good { background: rgba(52,211,153,.12); color: var(--good); border-color: rgba(52,211,153,.3); }
.pe-chip.warn { background: rgba(251,191,36,.12); color: var(--warn); border-color: rgba(251,191,36,.3); }
.pe-chip.risk { background: rgba(251,146,60,.12); color: var(--risk); border-color: rgba(251,146,60,.3); }
.pe-chip.bad { background: rgba(248,113,113,.12); color: var(--bad); border-color: rgba(248,113,113,.3); }
.pe-chip.muted { background: transparent; color: var(--muted); }

.pe-vertical { display: flex; gap: 14px; align-items: flex-start; background: var(--surface); border: 1px dashed var(--border-strong);
  border-radius: 12px; padding: 12px 14px; margin: 2px 0 14px 0; }
.pe-vertical .lbl { font-size: 0.7rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--faint); margin-bottom: 6px; }

.pe-kpis { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 4px 0 14px 0; }
.pe-kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; }
.pe-kpi .v { font-size: 1.35rem; font-weight: 800; color: var(--text); letter-spacing: -0.02em; }
.pe-kpi .l { font-size: 0.72rem; color: var(--muted); font-weight: 600; text-transform: uppercase; letter-spacing: .06em; }

.pe-selected { display: flex; align-items: center; justify-content: space-between; gap: 12px; background: var(--accent-soft);
  border: 1px solid rgba(124,131,255,.35); border-radius: 12px; padding: 12px 14px; margin: 14px 0 10px 0; }
.pe-selected .n { font-weight: 700; color: var(--text); }
.pe-selected .m { font-size: 0.8rem; color: var(--muted); margin-top: 2px; }
.pe-hint { display: flex; align-items: center; gap: 10px; color: var(--muted); font-size: 0.86rem; background: var(--surface);
  border: 1px dashed var(--border-strong); border-radius: 12px; padding: 12px 14px; margin-top: 12px; }

.pe-empty { text-align: center; padding: 48px 24px 40px 24px; }
.pe-empty .t { font-size: 1.1rem; font-weight: 700; color: var(--text); margin-top: 14px; }
.pe-empty .s { font-size: 0.88rem; color: var(--muted); margin: 6px auto 20px auto; max-width: 360px; line-height: 1.5; }
.pe-empty ol { text-align: left; display: inline-block; margin: 0 auto; padding: 0; list-style: none; counter-reset: s; }
.pe-empty li { counter-increment: s; color: var(--muted); font-size: 0.86rem; margin: 8px 0; display: flex; align-items: center; gap: 10px; }
.pe-empty li::before { content: counter(s); width: 22px; height: 22px; border-radius: 50%; display: grid; place-items: center;
  background: var(--surface-3); border: 1px solid var(--border-strong); font-size: 0.72rem; font-weight: 700; color: var(--text); }

.pe-firm { display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; margin-bottom: 14px; }
.pe-firm .name { font-size: 1.35rem; font-weight: 800; letter-spacing: -0.025em; color: var(--text); line-height: 1.2; }
.pe-firm .meta { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.pe-firm .blurb { color: var(--muted); font-size: 0.86rem; line-height: 1.5; margin-top: 10px; font-style: italic; }

.pe-grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
@media (max-width: 1100px) { .pe-grid2 { grid-template-columns: 1fr; } .pe-kpis { grid-template-columns: 1fr 1fr 1fr; } }
.pe-panel { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 14px; margin-bottom: 10px; }
.pe-cols { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 0 18px; }
@media (max-width: 1250px) { .pe-cols { grid-template-columns: 1fr; } }
.pe-hook { margin-bottom: 10px; }
.pe-panel .h { font-size: 0.7rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--faint); margin-bottom: 10px; }

.pe-contact { display: flex; align-items: center; gap: 12px; }
.pe-avatar { width: 44px; height: 44px; border-radius: 12px; display: grid; place-items: center; font-weight: 800; font-size: 0.95rem;
  background: var(--grad); color: #0A0E1A; flex-shrink: 0; }
.pe-contact .n { font-weight: 700; font-size: 1.02rem; color: var(--text); }
.pe-contact .r { font-size: 0.8rem; color: var(--muted); margin-top: 2px; }

.pe-row { display: flex; align-items: center; gap: 10px; padding: 7px 0; border-top: 1px solid var(--border); font-size: 0.86rem; }
.pe-row:first-of-type { border-top: none; }
.pe-row svg { color: var(--accent-2); flex-shrink: 0; }
.pe-row a, .pe-row span { color: var(--text) !important; text-decoration: none; overflow-wrap: anywhere; }
.pe-row .tag { color: var(--faint) !important; white-space: nowrap; }
.pe-row a.trunc { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; overflow-wrap: normal; }
.pe-row a:hover { color: var(--accent-2) !important; }
.pe-row .tag { margin-left: auto; font-size: 0.68rem; color: var(--faint); font-weight: 600; text-transform: uppercase; letter-spacing: .05em; }
.pe-none { color: var(--faint); font-size: 0.84rem; font-style: italic; }

.pe-officer { display: flex; justify-content: space-between; gap: 8px; padding: 6px 0; border-top: 1px solid var(--border); font-size: 0.84rem; }
.pe-officer:first-of-type { border-top: none; }
.pe-officer .who { color: var(--text); font-weight: 600; }
.pe-officer .since { color: var(--faint); font-size: 0.76rem; white-space: nowrap; }

.pe-hook { background: linear-gradient(135deg, rgba(124,131,255,.12), rgba(56,214,245,.06)); border: 1px solid rgba(124,131,255,.28);
  border-radius: 12px; padding: 14px 16px; }
.pe-hook .h { font-size: 0.7rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: #B9BDFF; }
.pe-hook .t { font-weight: 700; color: var(--text); margin: 4px 0 10px 0; }
.pe-hook ul { margin: 0; padding-left: 0; list-style: none; }
.pe-hook li { font-size: 0.85rem; color: var(--text); padding: 4px 0 4px 24px; position: relative; }
.pe-hook li::before { content: ""; position: absolute; left: 4px; top: 10px; width: 8px; height: 8px; border-radius: 50%; background: var(--grad); }

/* Workspace switch in sidebar */
[data-testid="stSidebar"] [role="radiogroup"] { gap: 6px; margin-bottom: 6px; }
[data-testid="stSidebar"] [role="radiogroup"] label { background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
  padding: 9px 12px !important; margin: 0 !important; width: 100%; }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { border-color: rgba(124,131,255,.55); background: var(--accent-soft); }
[data-testid="stSidebar"] [role="radiogroup"] label p { font-weight: 600 !important; font-size: .88rem !important; color: var(--text) !important;
  text-transform: none !important; letter-spacing: 0 !important; }
/* LinkedIn panel */
.st-key-card-linkedin { background: var(--surface); border: 1px solid rgba(10,102,194,.45) !important; border-radius: 12px;
  padding: 14px 14px 10px 14px; margin-bottom: 10px; }
.li-head { display: flex; gap: 10px; align-items: center; margin-bottom: 10px; }
.li-head .t { font-weight: 700; color: var(--text); font-size: .95rem; }
.li-head .s { font-size: .8rem; color: var(--muted); margin-top: 1px; }
.li-badge { width: 30px; height: 30px; border-radius: 7px; background: #0A66C2; color: #fff; font-weight: 800; font-size: .95rem;
  display: grid; place-items: center; flex-shrink: 0; font-family: Arial, sans-serif; }
.li-mini { width: 15px; height: 15px; border-radius: 3px; background: #0A66C2; color: #fff; font-weight: 800; font-size: .62rem;
  display: grid; place-items: center; flex-shrink: 0; font-family: Arial, sans-serif; }
/* Sidebar components */
.pe-brand { display: flex; align-items: center; gap: 12px; padding: 4px 0 18px 0; border-bottom: 1px solid var(--border); margin-bottom: 16px; }
.pe-logo { width: 40px; height: 40px; border-radius: 12px; background: var(--grad); display: grid; place-items: center; color: #0A0E1A;
  box-shadow: 0 10px 24px -10px rgba(124,131,255,.9); }
.pe-brand .n { font-weight: 800; font-size: 1.05rem; color: var(--text); letter-spacing: -0.02em; }
.pe-brand .s { font-size: 0.75rem; color: var(--muted); }
.pe-side-h { font-size: 0.68rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--faint); margin: 18px 0 8px 0; }
.pe-status { display: flex; align-items: center; justify-content: space-between; font-size: 0.84rem; color: var(--text); padding: 7px 0; }
.pe-status .st { display: inline-flex; align-items: center; gap: 6px; font-size: 0.76rem; font-weight: 600; }
.pe-status .st.ok { color: var(--good); } .pe-status .st.off { color: var(--bad); } .pe-status .st.idle { color: var(--muted); }
.pe-status .st::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
.pe-stats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
.pe-stat { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 10px; text-align: center; }
.pe-stat .v { font-weight: 800; font-size: 1.1rem; color: var(--text); }
.pe-stat .l { font-size: 0.64rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; font-weight: 600; margin-top: 2px; }

/* Login */
.pe-login-head { text-align: center; margin: 8vh 0 22px 0; }
.pe-login-head .pe-logo { width: 54px; height: 54px; margin: 0 auto 16px auto; border-radius: 16px; }
.pe-login-head .t { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.03em; color: var(--text); }
.pe-login-head .s { color: var(--muted); font-size: 0.92rem; margin-top: 6px; }
</style>
"""

_ICON_PATHS = {
    "mail": '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "globe": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
    "pin": '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
    "lock": '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "pointer": '<path d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z"/>',
}


def _full_width_kwargs() -> Dict[str, Any]:
    """Full-width buttons: 'width' on Streamlit 1.46+, 'use_container_width' before that."""
    import inspect
    try:
        if "width" in inspect.signature(st.button).parameters:
            return {"width": "stretch"}
    except (TypeError, ValueError):
        pass
    return {"use_container_width": True}


FULL_WIDTH = _full_width_kwargs()


def icon(name: str, size: int = 16, stroke: float = 2) -> str:
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
        f' stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round">{_ICON_PATHS[name]}</svg>'
    )


def esc(value: Any) -> str:
    """Escapes scraped/registry text before it goes into HTML."""
    return html_lib.escape(str(value if value is not None else ""), quote=True)


def render_html(markup: str, target=None) -> None:
    """Renders HTML via markdown. Lines are flattened so markdown never treats indentation as code."""
    flat = "".join(line.strip() for line in markup.splitlines())
    (target or st).markdown(flat, unsafe_allow_html=True)


def inject_css() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)


def chip(text: str, tone: str = "") -> str:
    return f'<span class="pe-chip {tone}">{esc(text)}</span>'


def section_header(num: str, title: str, subtitle: str = "") -> None:
    render_html(
        f'<div class="pe-section"><div class="badge">{num}</div><div>'
        f'<div class="t">{esc(title)}</div>'
        + (f'<div class="s">{esc(subtitle)}</div>' if subtitle else "")
        + "</div></div>"
    )


def hero_html(active_step: int) -> str:
    steps = ["Load", "Pick", "Tailor", "Send"]
    parts = []
    for i, label in enumerate(steps, start=1):
        state = "done" if i < active_step else "active" if i == active_step else ""
        num = icon("check", 12, 3) if state == "done" else str(i)
        parts.append(f'<div class="pe-step {state}"><span class="num">{num}</span>{label}</div>')
    stepper = '<div class="pe-step-sep"></div>'.join(parts)
    return (
        '<div class="pe-hero"><div>'
        '<div class="pe-eyebrow"><span class="dot"></span>Zoho CRM · Existing customers</div>'
        '<div class="pe-title">Customer <span>Growth</span></div>'
        '<div class="pe-sub">Keep in touch with the customers you already have: spot what each account is missing,'
        ' then send a tailored, on-brand email through Zoho.</div>'
        f'</div><div class="pe-stepper">{stepper}</div></div>'
    )


def initials(name: str) -> str:
    words = [w for w in re.split(r"[\s&/]+", name or "") if w and w[0].isalpha()]
    return ("".join(w[0] for w in words[:2]) or "?").upper()


# ==========================================
# 0. PASSWORD GATEWAY (STREAMLIT SECRETS)
# ==========================================


def check_password() -> bool:
    # Fail CLOSED: if the secret is missing or misconfigured, nobody gets in.
    try:
        configured_password = st.secrets["APP_PASSWORD"]
    except Exception:
        configured_password = None
    if not configured_password:
        st.set_page_config(page_title=f"{APP_NAME} · Locked", page_icon="🎯", layout="centered")
        inject_css()
        render_html(
            f'<div class="pe-login-head"><div class="pe-logo">{icon("lock", 24, 2.2)}</div>'
            '<div class="t">App locked</div>'
            '<div class="s">APP_PASSWORD isn\'t set in Streamlit Secrets, so access is blocked.</div></div>'
        )
        st.error("Add APP_PASSWORD under App settings → Secrets, then reload.")
        return False

    def password_entered():
        if hmac.compare_digest(
            st.session_state.get("password", "").encode("utf-8"),
            str(configured_password).encode("utf-8"),
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.set_page_config(page_title=f"{APP_NAME} · Sign in", page_icon="🎯", layout="centered")
    inject_css()
    _, mid, _ = st.columns([1, 2.2, 1])
    with mid:
        render_html(
            f'<div class="pe-login-head"><div class="pe-logo">{icon("target", 26, 2.2)}</div>'
            f'<div class="t">{APP_NAME}</div>'
            f'<div class="s">{APP_TAGLINE} · Authorised users only</div></div>'
        )
        with st.container(key="card-login"):
            with st.form("Credentials", border=False):
                st.text_input("Access password", type="password", key="password",
                              placeholder="Enter your password")
                st.form_submit_button("Sign in", on_click=password_entered,
                                      type="primary", **FULL_WIDTH)
            if (
                "password_correct" in st.session_state
                and not st.session_state["password_correct"]
            ):
                st.error("Incorrect password. Please try again.")

    return False


if not check_password():
    st.stop()



# ==========================================
# SHARED STORAGE (GitHub JSON)
# ==========================================
def _secret_value(key: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(key, default) or default)
    except Exception:
        return default


class SentLog:
    """Stores {company_number: record} of firms that have been emailed.

    Permanent: a JSON file in a private GitHub repo (set GITHUB_TOKEN + GITHUB_REPO in Secrets).
    Fallback: a local file, which Streamlit Cloud wipes whenever the app restarts or redeploys.
    """

    def __init__(self, path_secret: str = "GITHUB_LOG_PATH", default_path: str = "sent_log.json",
                 local_name: str = ".sent_log.json") -> None:
        self.token = _secret_value("GITHUB_TOKEN")
        self.repo = _secret_value("GITHUB_REPO")  # e.g. "sammyatt2010-hub/prospect-engine-data"
        self.branch = _secret_value("GITHUB_BRANCH", "main")
        self.path = _secret_value(path_secret, default_path)
        self.backend = "github" if (self.token and self.repo) else "local"
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            base_dir = os.getcwd()
        self.local_path = os.path.join(base_dir, local_name)
        self.last_error: Optional[str] = None

    # ---------- GitHub backend ----------
    def _url(self) -> str:
        return f"https://api.github.com/repos/{self.repo}/contents/{self.path}"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _gh_read(self) -> Tuple[Dict[str, Any], Optional[str]]:
        resp = requests.get(self._url(), headers=self._headers(), params={"ref": self.branch}, timeout=10)
        if resp.status_code == 404:
            return {}, None  # File doesn't exist yet; first write creates it
        if resp.status_code != 200:
            raise RuntimeError(self._describe(resp.status_code))
        payload = resp.json()
        content = base64.b64decode(payload.get("content", "") or b"").decode("utf-8-sig").strip()
        if not content or content in ("[]", "null"):
            return {}, payload.get("sha")  # Emptied by hand on GitHub: treat as a fresh start
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise RuntimeError(f"{self.path} on GitHub isn't valid JSON. Replace its contents with {{}} to start fresh.")
        return (data if isinstance(data, dict) else {}), payload.get("sha")

    def _gh_write(self, data: Dict[str, Any], sha: Optional[str], message: str) -> int:
        body: Dict[str, Any] = {
            "message": message,
            "content": base64.b64encode(json.dumps(data, indent=2, sort_keys=True).encode("utf-8")).decode("ascii"),
            "branch": self.branch,
        }
        if sha:
            body["sha"] = sha
        resp = requests.put(self._url(), headers=self._headers(), json=body, timeout=12)
        return resp.status_code

    @staticmethod
    def _describe(code: int) -> str:
        return {
            401: "GitHub rejected the token (401). Check GITHUB_TOKEN in Secrets.",
            403: "GitHub token lacks permission (403). It needs Contents: Read and write on the repo.",
            404: "GitHub repo not found (404). Check GITHUB_REPO in Secrets.",
        }.get(code, f"GitHub returned an error ({code}).")

    # ---------- Local backend ----------
    def _local_read(self) -> Dict[str, Any]:
        try:
            with open(self.local_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                return data if isinstance(data, dict) else {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _local_write(self, data: Dict[str, Any]) -> None:
        tmp = self.local_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
        os.replace(tmp, self.local_path)

    # ---------- Public API ----------
    def load(self) -> Dict[str, Any]:
        self.last_error = None
        try:
            return self._gh_read()[0] if self.backend == "github" else self._local_read()
        except Exception as exc:  # Never let the log break the app
            self.last_error = str(exc) if isinstance(exc, RuntimeError) else f"Couldn't load sent log ({exc.__class__.__name__})."
            return {}

    def apply(self, changes: Dict[str, Optional[Dict[str, Any]]], message: str) -> Dict[str, Any]:
        """Applies {company_number: record or None (= un-mark)} and returns the latest full log.
        Re-reads before writing, so two people using the app at once don't overwrite each other."""
        self.last_error = None

        def merge(data: Dict[str, Any]) -> Dict[str, Any]:
            for key, record in changes.items():
                if record is None:
                    data.pop(key, None)
                else:
                    data[key] = record
            return data

        if self.backend == "local":
            data = merge(self._local_read())
            self._local_write(data)
            return data

        for _attempt in range(3):
            data, sha = self._gh_read()
            data = merge(data)
            status = self._gh_write(data, sha, message)
            if status in (200, 201):
                return data
            if status not in (409, 422):  # 409/422 = someone else saved first; re-read and retry
                raise RuntimeError(self._describe(status))
        raise RuntimeError("GitHub was busy saving the sent log. Please try again.")


def now_uk() -> datetime:
    try:
        return datetime.now(ZoneInfo("Europe/London"))
    except Exception:
        return datetime.now()


def sent_label(record: Optional[Dict[str, Any]]) -> str:
    """'✓ 25 Sep' for the tables."""
    if not record:
        return ""
    try:
        return "✓ " + datetime.fromisoformat(record.get("sent_at", "")).strftime("%d %b").lstrip("0")
    except ValueError:
        return "✓ Sent"




# ==========================================
# ZOHO CRM CONNECTOR
# ==========================================
ZOHO_MAX_RECORDS = 10000
ZOHO_PAGE = 2000  # COQL maximum per call
ZOHO_SEND_LIMIT = 100  # Zoho's Send Mail API allows 100 emails a day
ZOHO_SCOPE = ("ZohoCRM.modules.accounts.ALL,ZohoCRM.modules.contacts.READ,ZohoCRM.modules.notes.CREATE,"
              "ZohoCRM.coql.READ,ZohoCRM.settings.fields.READ,ZohoCRM.org.READ,"
              "ZohoCRM.send_mail.contacts.CREATE,ZohoCRM.settings.emails.READ")


class ZohoError(RuntimeError):
    pass


class ZohoCRM:
    """Minimal Zoho CRM v8 client using a Self Client refresh token (EU data centre by default)."""

    def __init__(self) -> None:
        self.client_id = _secret_value("ZOHO_CLIENT_ID")
        self.client_secret = _secret_value("ZOHO_CLIENT_SECRET")
        self.refresh_token = _secret_value("ZOHO_REFRESH_TOKEN")
        self.accounts_url = _secret_value("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.eu").rstrip("/")
        self.api_domain = _secret_value("ZOHO_API_DOMAIN", "https://www.zohoapis.eu").rstrip("/")
        self.crm_url = _secret_value("ZOHO_CRM_URL", "https://crm.zoho.eu").rstrip("/")
        self.configured = bool(self.client_id and self.client_secret and self.refresh_token)
        # Client ID + secret in Secrets but no refresh token yet: the app can do the one-off swap itself
        self.can_setup = bool(self.client_id and self.client_secret) and not self.refresh_token

    # ---------- one-off setup: swap a Self Client code for a refresh token ----------
    def exchange_code(self, code: str) -> Dict[str, str]:
        """Returns {'refresh_token': ...} or {'error': plain-English reason}."""
        try:
            resp = requests.post(
                f"{self.accounts_url}/oauth/v2/token",
                data={"grant_type": "authorization_code", "client_id": self.client_id,
                      "client_secret": self.client_secret, "code": code.strip()},
                timeout=15,
            )
            data = resp.json()
        except requests.exceptions.RequestException as exc:
            return {"error": f"Couldn't reach Zoho ({exc.__class__.__name__}). Try again in a moment."}
        except ValueError:
            return {"error": f"Zoho sent an unreadable reply (HTTP {resp.status_code}). Check the Self Client is on api-console.zoho.eu."}
        if data.get("refresh_token"):
            return {"refresh_token": data["refresh_token"]}
        if data.get("access_token"):
            return {"error": "Zoho gave a short-lived token but no refresh token. Generate a new code and try again."}
        err = str(data.get("error") or f"HTTP {resp.status_code}")
        hints = {
            "invalid_code": "The code has expired or was already used. Codes last only a few minutes and work once, so generate a fresh one and paste it straight in.",
            "invalid_client": "Zoho doesn't recognise ZOHO_CLIENT_ID. Copy it again from the Self Client's Client Secret tab. If the Self Client was made on api-console.zoho.com (not .eu), make a new one on api-console.zoho.eu.",
            "invalid_client_secret": "ZOHO_CLIENT_SECRET doesn't match the client ID. Copy it again from the Self Client's Client Secret tab (watch for stray spaces).",
        }
        return {"error": f"Zoho said: {err}. " + hints.get(err, "Generate a fresh code and try again. If it keeps failing, check the client ID and secret in Secrets.")}

    # ---------- auth ----------
    def _token(self, force: bool = False) -> str:
        cached = st.session_state.get("zoho_token")
        if cached and not force and cached[1] > time.time() + 60:
            return cached[0]
        try:
            resp = requests.post(
                f"{self.accounts_url}/oauth/v2/token",
                params={"refresh_token": self.refresh_token, "client_id": self.client_id,
                        "client_secret": self.client_secret, "grant_type": "refresh_token"},
                timeout=12,
            )
            data = resp.json()
        except requests.exceptions.RequestException as exc:
            raise ZohoError(f"Couldn't reach Zoho to sign in ({exc.__class__.__name__}).")
        except ValueError:
            raise ZohoError("Zoho sent an unreadable sign-in response.")
        if "access_token" not in data:
            err = data.get("error", "unknown error")
            hint = {
                "invalid_code": "The refresh token is invalid or was revoked. Generate a new one in api-console.zoho.eu.",
                "invalid_client": "ZOHO_CLIENT_ID / ZOHO_CLIENT_SECRET don't match. Check them in Secrets.",
            }.get(err, "Check the Zoho secrets and that the Self Client is in the EU data centre.")
            raise ZohoError(f"Zoho sign-in failed ({err}). {hint}")
        if data.get("api_domain"):
            self.api_domain = data["api_domain"].rstrip("/")
        st.session_state["zoho_token"] = (data["access_token"], time.time() + int(data.get("expires_in", 3600)))
        return data["access_token"]

    def _request(self, method: str, path: str, **kwargs) -> Optional[Dict[str, Any]]:
        for attempt in (0, 1):
            headers = {"Authorization": f"Zoho-oauthtoken {self._token(force=attempt == 1)}"}
            try:
                resp = requests.request(method, f"{self.api_domain}{path}", headers=headers, timeout=20, **kwargs)
            except requests.exceptions.RequestException as exc:
                raise ZohoError(f"Couldn't reach Zoho CRM ({exc.__class__.__name__}).")
            if resp.status_code == 204:
                return None  # No records
            try:
                body = resp.json()
            except ValueError:
                body = {}
            code = str(body.get("code", ""))
            if resp.status_code == 401 and code in ("INVALID_TOKEN", "AUTHENTICATION_FAILURE") and attempt == 0:
                continue  # Token expired early: refresh once and retry
            if resp.status_code >= 400:
                row = (body.get("data") or [{}])[0] if isinstance(body.get("data"), list) else {}
                code = code or str(row.get("code", ""))
                msg = body.get("message") or row.get("message") or code or f"HTTP {resp.status_code}"
                if code == "OAUTH_SCOPE_MISMATCH":
                    msg = "The Zoho token is missing a permission. Regenerate it with the scopes listed in the setup notes."
                raise ZohoError(f"Zoho CRM error: {msg}")
            return body
        raise ZohoError("Zoho CRM rejected the sign-in.")

    # ---------- reads ----------
    def fields(self, module: str) -> Dict[str, Dict[str, Any]]:
        body = self._request("GET", "/crm/v8/settings/fields", params={"module": module}) or {}
        return {f["api_name"]: f for f in body.get("fields", [])}

    @staticmethod
    def picklist(fields: Dict[str, Dict[str, Any]], api_name: str) -> List[str]:
        """The options as people see them in Zoho (renamed standard options keep an old 'actual' value)."""
        values = (fields.get(api_name) or {}).get("pick_list_values") or []
        out = [v.get("display_value") or v.get("actual_value") for v in values]
        return [v for v in out if v and v != "-None-"]

    @staticmethod
    def picklist_aliases(fields: Dict[str, Dict[str, Any]], api_name: str) -> Dict[str, str]:
        """{any spelling Zoho may use (display or actual value): display value}."""
        out: Dict[str, str] = {}
        for v in (fields.get(api_name) or {}).get("pick_list_values") or []:
            shown = v.get("display_value") or v.get("actual_value")
            for alias in (v.get("display_value"), v.get("actual_value")):
                if alias and shown:
                    out[alias] = shown
        return out

    def org_domain(self) -> Optional[str]:
        try:
            body = self._request("GET", "/crm/v8/org") or {}
            org = (body.get("org") or [{}])[0]
            return org.get("domain_name")
        except ZohoError:
            return None

    def query_all(self, module: str, fields: List[str], where: str, order: str = "Created_Time") -> List[Dict[str, Any]]:
        """Every matching record (up to ZOHO_MAX_RECORDS) via COQL, 2,000 per call."""
        out: List[Dict[str, Any]] = []
        offset = 0
        while offset < ZOHO_MAX_RECORDS:
            query = (f"select {', '.join(fields)} from {module} where {where} "
                     f"order by {order} asc limit {offset}, {ZOHO_PAGE}")
            try:
                body = self._request("POST", "/crm/v8/coql", json={"select_query": query})
            except ZohoError:
                if out:
                    break
                raise
            if not body:
                break
            out.extend(body.get("data") or [])
            if not (body.get("info") or {}).get("more_records"):
                break
            offset += ZOHO_PAGE
        return out

    def get_records(self, module: str, fields: List[str]) -> Dict[str, Dict[str, Any]]:
        """{id: record} for all records, via the Get Records API (for field types COQL can't read, like files)."""
        out: Dict[str, Dict[str, Any]] = {}
        params: Dict[str, Any] = {"fields": ",".join(fields), "per_page": 200}
        page = 1
        while len(out) < ZOHO_MAX_RECORDS:
            body = self._request("GET", f"/crm/v8/{module}", params=dict(params, page=page) if "page_token" not in params
                                 else params) or {}
            for r in body.get("data") or []:
                out[str(r.get("id"))] = r
            info = body.get("info") or {}
            if not info.get("more_records"):
                break
            if info.get("next_page_token"):
                params["page_token"] = info["next_page_token"]
                params.pop("page", None)
            else:
                page += 1
        return out

    # ---------- writes (phase 2): send, fill blanks, notes ----------
    @staticmethod
    def _row_result(body: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        row = ((body or {}).get("data") or [{}])[0]
        if row.get("status") != "success":
            msg = row.get("message") or row.get("code") or "unknown error"
            raise ZohoError(f"Zoho CRM error: {msg}")
        return row.get("details") or {}

    def from_addresses(self) -> List[Dict[str, Any]]:
        body = self._request("GET", "/crm/v8/settings/emails/actions/from_addresses") or {}
        return [a for a in body.get("from_addresses", []) if a.get("email")]

    def send_mail(self, module: str, record_id: str, sender: Dict[str, Any], to_email: str, to_name: str,
                  subject: str, html: str, attachment_ids: Optional[List[str]] = None) -> str:
        mail: Dict[str, Any] = {
            "from": {"user_name": sender.get("user_name") or "", "email": sender["email"]},
            "to": [{"user_name": to_name or "", "email": to_email}],
            "subject": subject, "content": html, "mail_format": "html",
        }
        if sender.get("type") == "org_email":
            mail["org_email"] = True
        if attachment_ids:
            mail["attachments"] = [{"id": a} for a in attachment_ids]
        body = self._request("POST", f"/crm/v8/{module}/{record_id}/actions/send_mail", json={"data": [mail]})
        return self._row_result(body).get("message_id", "")

    def add_note(self, module: str, record_id: str, title: str, content: str) -> None:
        note = {"Note_Title": title, "Note_Content": content,
                "Parent_Id": {"module": {"api_name": module}, "id": record_id}}
        self._row_result(self._request("POST", f"/crm/v8/{module}/{record_id}/Notes", json={"data": [note]}))

    def record_url(self, module: str, record_id: str) -> str:
        dom = st.session_state.get("zoho_org_domain")
        base = f"{self.crm_url}/crm/{dom}" if dom else f"{self.crm_url}/crm"
        return f"{base}/tab/{module}/{record_id}"


# ==========================================
# 1. BRANDS, INDUSTRIES & OFFERS
# ==========================================

ACCOUNT_TYPES_DEFAULT = ["SYC Customer", "SY Plus Customer", "South Wales Comms"]
# How each brand's customer type is recognised, whatever exact spelling Zoho uses
BRAND_PATTERNS = {"SYC Customer": ("syc",), "SY Plus Customer": ("syplus", "sy+"),
                  "South Wales Comms": ("southwales", "swcomms", "swc")}


def _norm(v: str) -> str:
    return re.sub(r"[^a-z0-9+]", "", (v or "").lower())


def brand_key(value: str) -> Optional[str]:
    """Which brand a customer-type value belongs to (e.g. 'SYC Customer', 'SYC - Customer' -> 'SYC Customer')."""
    n = _norm(value)
    for key, pats in BRAND_PATTERNS.items():
        if any(n.startswith(p) or p in n for p in pats):
            return key
    return None

# Each Account Type is emailed as its own brand. Contact details for SY Plus and South Wales Comms
# are filled in once under "Brand details" in the app (saved to GitHub), until then SY Comms is used.
DEFAULT_BRANDS: Dict[str, Dict[str, Any]] = {
    "SYC Customer": {
        "name": "SY Communications", "word1": "SY", "word2": "Communications",
        "primary": "#1f1450", "accent": "#00b5a3", "tagline": "Business phones that work with your software",
        "phone": "01743 667419", "email": "hello@sycomms.co.uk", "website": "www.sycomms.co.uk",
        "address": "Suite C, Jupiter House, Shrewsbury SY2 6LG",
    },
    "SY Plus Customer": {
        "name": "SY Plus", "word1": "SY", "word2": "Plus",
        "primary": "#1f1450", "accent": "#7c83ff", "tagline": "Business phones that work with your software",
        "phone": "", "email": "", "website": "", "address": "",
    },
    "South Wales Comms": {
        "name": "South Wales Comms", "word1": "South Wales", "word2": "Comms",
        "primary": "#10233f", "accent": "#e0473b", "tagline": "Business phones that work with your software",
        "phone": "", "email": "", "website": "", "address": "",
    },
}
BRAND_FIELDS = [("name", "Brand name"), ("word1", "Logo text (white part)"), ("word2", "Logo text (coloured part)"),
                ("tagline", "Tagline"), ("primary", "Main colour"), ("accent", "Accent colour"),
                ("phone", "Phone"), ("email", "Email (replies & sending)"), ("website", "Website"),
                ("address", "Address")]
CALLSCOPE_URL_DEFAULT = "https://callscope-sycomms.streamlit.app/"

# Industry profiles: matched against the Zoho Industry value (then the account name)
INDUSTRY_PROFILES: List[Dict[str, Any]] = [
    {"name": "Estate & Lettings", "words": ("estate agent", "estate", "letting", "property", "real estate"),
     "plural": "estate and lettings agents", "crms": ["Reapit", "Alto", "Street"]},
    {"name": "Dental", "words": ("dental", "dentist", "orthodont"),
     "plural": "dental practices", "crms": ["Dentally", "EXACT", "Carestream R4"]},
    {"name": "Legal", "words": ("legal", "law", "solicitor", "lawyer", "conveyanc"),
     "plural": "law firms", "crms": ["Clio", "LEAP", "Actionstep"]},
    {"name": "Accountancy", "words": ("accountan", "accounting", "bookkeep", "tax", "audit", "payroll"),
     "plural": "accountancy practices", "crms": ["Xero Practice Manager", "IRIS", "CCH"]},
    {"name": "Medical & Healthcare", "words": ("medical", "clinic", "healthcare", "health care", "gp ", "physio",
                                               "pharma", "care home", "hospital "),
     "plural": "clinics and care providers", "crms": ["EMIS Web", "SystmOne", "Semble"]},
    {"name": "Recruitment", "words": ("recruit", "staffing", "employment agency"),
     "plural": "recruitment agencies", "crms": ["Bullhorn", "Vincere", "Mercury"]},
    {"name": "Automotive", "words": ("automotive", "garage", "motor", "car dealer", "vehicle", "tyre"),
     "plural": "garages and dealerships", "crms": ["Keyloop", "MAM Autowork", "GaragePro"]},
    {"name": "Insurance & Financial", "words": ("insurance", "financial", "finance", "mortgage", "broker",
                                                "wealth", "banking", "investment"),
     "plural": "brokers and financial advisers", "crms": ["Acturis", "Intelliflo", "Salesforce"]},
    {"name": "Veterinary", "words": ("veterinar", "vets", "vet ", "animal"),
     "plural": "veterinary practices", "crms": ["RxWorks", "Provet Cloud", "VetIT"]},
    {"name": "Opticians", "words": ("optic", "optometr", "eyecare"),
     "plural": "opticians", "crms": ["Optix", "Ocuco", "Opticabase"]},
    {"name": "Hospitality", "words": ("hotel", "hospitality", "restaurant", "leisure", "pub", "catering"),
     "plural": "hospitality businesses", "crms": ["ResDiary", "Guestline", "OpenTable"]},
    {"name": "Retail", "words": ("retail", "shop", "store", "ecommerce", "e-commerce", "wholesale"),
     "plural": "retailers", "crms": ["Shopify", "Lightspeed", "Microsoft 365"]},
    {"name": "Construction & Trades", "words": ("construct", "building", "builder", "trade", "plumb", "electric",
                                                "engineering", "manufactur", "roofing", "joinery"),
     "plural": "trade and construction firms", "crms": ["simPRO", "Commusoft", "Xero"]},
    {"name": "Education", "words": ("education", "school", "college", "nursery", "training", "academy"),
     "plural": "schools and training providers", "crms": ["Arbor", "SIMS", "Microsoft Teams"]},
    {"name": "Charity", "words": ("charity", "non-profit", "nonprofit", "not for profit", "church"),
     "plural": "charities", "crms": ["Salesforce", "Beacon", "Donorfy"]},
    {"name": "IT & Technology", "words": ("technology", "software", "it services", "computer", "telecom", "digital"),
     "plural": "technology firms", "crms": ["HubSpot", "Salesforce", "ConnectWise"]},
]
GENERAL_PROFILE = {"name": "General Business", "words": (), "plural": "businesses",
                   "crms": ["Microsoft Teams", "HubSpot", "Salesforce"]}
FALSE_FRIENDS = ("health and safety", "health & safety", "fire safety", "tree surgery", "law enforcement")
CUSTOMER_FACING = {"Estate & Lettings", "Dental", "Legal", "Medical & Healthcare", "Recruitment", "Automotive",
                   "Insurance & Financial", "Veterinary", "Opticians", "Hospitality", "Retail", "Accountancy"}
CCTV_FRIENDLY = {"Dental", "Medical & Healthcare", "Automotive", "Hospitality", "Retail", "Construction & Trades",
                 "Veterinary", "Opticians", "Education"}


def industry_profile(industry: str, name: str = "") -> Dict[str, Any]:
    for text in (industry or "", name or ""):
        hay = f" {text.lower()} "
        for phrase in FALSE_FRIENDS:
            hay = hay.replace(phrase, " ")
        for prof in INDUSTRY_PROFILES:
            if any(re.search(r"(?<![a-z])" + re.escape(w), hay) for w in prof["words"]):
                return prof
    return GENERAL_PROFILE


# ---- Zoho field mapping: which Account field holds which service ----
# (slot, label, keywords to auto-match on the Zoho field label, kind)
MAP_SLOTS: List[Tuple[str, str, Tuple[str, ...], str]] = [
    ("contract_end", "Contract end date", ("contract end", "end date", "renewal date", "renewal", "expiry",
                                           "expires", "term end"), "date"),
    ("contract_start", "Contract start date", ("contract start", "start date", "go live", "live date",
                                               "commence"), "date"),
    ("contract_term", "Contract term (months)", ("term months", "contract term", "term (months)"), "any"),
    ("users", "Number of users / seats", ("users", "seats", "extensions", "licences", "licenses", "handsets"), "any"),
    ("broadband", "Broadband (any date/value = has it)", ("broadband", "internet", "fibre", "fttp", "fttc", "leased line",
                                               "connectivity"), "any"),
    ("mobiles", "Mobiles (any date/value = has it)", ("mobile", "sim"), "any"),
    ("call_scope", "Call Scope", ("call scope", "callscope", "call analytics", "call recording"), "any"),
    ("integration", "CRM integration", ("integration", "crm connect", "screen pop", "screen-pop"), "any"),
    ("cctv", "CCTV", ("cctv", "camera"), "any"),
    ("headsets", "Headsets", ("headset",), "any"),
    ("networking", "Networking / Wi-Fi (any value = has it)", ("wifi", "wi-fi", "network", "firewall", "router"), "any"),
    ("services", "Services list (a field listing everything they have)", ("services", "products", "solutions"),
     "any"),
]
SLOT_LABEL = {s[0]: s[1] for s in MAP_SLOTS}
DATE_TYPES = {"date", "datetime"}
# Words that show a service in a free-text/multi-select "Services" field
SERVICE_WORDS = {
    "broadband": ("broadband", "fibre", "fttp", "fttc", "leased line", "internet", "connectivity", "sogea"),
    "mobiles": ("mobile", "sim"),
    "call_scope": ("call scope", "callscope", "call recording", "analytics"),
    "integration": ("integration", "screen pop", "screen-pop", "crm connect"),
    "cctv": ("cctv", "camera"),
    "headsets": ("headset",),
    "networking": ("wifi", "wi-fi", "network", "firewall", "router", "switch", "it services", "it support"),
}
NO_VALUES = {"", "no", "none", "n/a", "na", "0", "-none-", "false", "not taken", "nil", "-"}


# SY Comms' own Zoho Account fields (by label), used first. Any date or value in them = they have it,
# e.g. a "BB Install Date" means they have broadband with us.
SYC_FIELD_DEFAULTS: Dict[str, Tuple[str, ...]] = {
    "contract_end": ("Contract Date End", "END DATE"),
    "contract_start": ("Contract Signed Date", "START DATE"),
    "contract_term": ("Contract Term Months",),
    "users": ("No. of System Users",),
    "broadband": ("BB Install Date",),
    "mobiles": ("Latest Mobile Invoice",),
    "networking": ("IT SERVICES CUSTOMER",),
    "services": ("Current Products",),
}


def auto_field_map(fields: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """Which Account field holds each slot: SY Comms' known fields first, then a guess from the labels."""
    used: Set[str] = set()
    out: Dict[str, str] = {}
    by_label = {(f.get("field_label") or api).strip().lower(): api for api, f in fields.items()}
    for slot, labels in SYC_FIELD_DEFAULTS.items():
        for label in labels:
            api = by_label.get(label.lower())
            if api and api not in used:
                out[slot] = api
                used.add(api)
                break
    for slot, _, words, kind in MAP_SLOTS:
        if slot in out:
            continue
        for api, f in fields.items():
            label = (f.get("field_label") or api).lower()
            if api in used or api in ("Account_Name", "Account_Type", "Industry", "Description"):
                continue
            if any(brand_key(v.get("actual_value") or "") for v in (f.get("pick_list_values") or [])):
                continue  # That's the customer-type field, not a service
            if kind == "date" and (f.get("data_type") or "") not in DATE_TYPES:
                continue
            if any(w in label for w in words):
                out[slot] = api
                used.add(api)
                break
    return out


def value_text(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if isinstance(v, list):
        return ", ".join(value_text(x) for x in v if value_text(x))
    if isinstance(v, dict):
        return str(v.get("name") or v.get("display_value") or v.get("id") or "")
    return str(v)


def has_value(v: Any) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v > 0
    if isinstance(v, list):
        return any(has_value(x) for x in v)
    return value_text(v).strip().lower() not in NO_VALUES


def parse_date(v: Any) -> Optional[datetime]:
    s = value_text(v)[:10]
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        return None


def months_between(a: datetime, b: datetime) -> float:
    return (b - a).days / 30.44


# ---- Offers ----
OFFER_ORDER = ["renewal", "integration", "call_scope", "mobiles", "broadband", "cctv", "headsets", "networking"]
OFFER_TITLES = {
    "renewal": "Contract review", "integration": "CRM integration", "call_scope": "Call Scope",
    "mobiles": "Business mobiles", "broadband": "Business broadband", "cctv": "CCTV",
    "headsets": "Wireless headsets", "networking": "Wi-Fi & networking",
}


def offer_line(key: str, prof: Dict[str, Any]) -> str:
    crms = prof["crms"]
    crms_str = ", ".join(crms[:2]) + f" or {crms[2]}" if len(crms) >= 3 else " or ".join(crms)
    return {
        "integration": f"Connect your phones to {crms_str}, so caller details pop up on screen and every call is"
                       " logged automatically.",
        "call_scope": "See every call in one place, including missed calls, busy times and recordings, so no"
                      " enquiry slips through the net.",
        "mobiles": "Business mobiles on the same account and bill as your phones, with calls between them included.",
        "broadband": "Business-grade broadband with UK support, plus a backup option so your phones never go down.",
        "cctv": "HD cameras you can check from your phone, installed and looked after by the same team.",
        "headsets": "Wireless headsets so the team can move around mid-call, with clearer sound for your customers.",
        "networking": "Managed Wi-Fi and firewall, so the whole office stays fast and secure.",
    }.get(key, "")


def account_snapshot(acct: Dict[str, Any], fmap: Dict[str, str]) -> Dict[str, Any]:
    """What we know about an account: its services (True/False/None = unknown), contract dates, profile."""
    services_text = value_text(acct.get(fmap["services"])).lower() if fmap.get("services") else ""
    has: Dict[str, Optional[bool]] = {}
    for key in ("broadband", "mobiles", "call_scope", "integration", "cctv", "headsets", "networking"):
        api = fmap.get(key)
        in_products = any(w in services_text for w in SERVICE_WORDS[key]) if services_text else False
        if api:
            # Their own field (a date, value or file) or a mention in Current Products both count
            has[key] = has_value(acct.get(api)) or in_products
        elif fmap.get("services"):
            has[key] = in_products
        else:
            has[key] = None
    today = now_uk().replace(tzinfo=None)
    end = parse_date(acct.get(fmap["contract_end"])) if fmap.get("contract_end") else None
    start = parse_date(acct.get(fmap["contract_start"])) if fmap.get("contract_start") else None
    if not end and start and fmap.get("contract_term"):
        try:  # No end date typed in: work it out from the signed date + term
            term = int(float(value_text(acct.get(fmap["contract_term"])) or 0))
        except ValueError:
            term = 0
        if term > 0:
            y, m = divmod(start.month - 1 + term, 12)
            end = start.replace(year=start.year + y, month=m + 1, day=min(start.day, 28))
    since = start or parse_date(acct.get("Created_Time"))
    users_raw = acct.get(fmap["users"]) if fmap.get("users") else None
    try:
        users = int(float(value_text(users_raw))) if value_text(users_raw) else None
    except ValueError:
        users = None
    prof = industry_profile(value_text(acct.get("Industry")), acct.get("Account_Name") or "")
    return {
        "has": has, "end": end, "start": start, "since": since, "users": users, "profile": prof,
        "months_left": months_between(today, end) if end else None,
        "months_in": months_between(since, today) if since else None,
        "services_text": services_text,
    }


def rank_offers(snap: Dict[str, Any]) -> List[Tuple[str, int, str]]:
    """[(offer, score, why)] best first. Unknown services still appear, lower down."""
    prof, has, out = snap["profile"], snap["has"], []
    ml = snap["months_left"]
    if ml is not None and -12 <= ml <= 12:
        out.append(("renewal", 95 if ml <= 6 else 80,
                    f"Contract {'ended' if ml < 0 else 'ends'} {snap['end'].strftime('%b %Y')}"))
    base = {"integration": 78 if prof is not GENERAL_PROFILE else 55,
            "call_scope": 74 if prof["name"] in CUSTOMER_FACING else 62,
            "mobiles": 66, "broadband": 60,
            "cctv": 48 if prof["name"] in CCTV_FRIENDLY else 30,
            "headsets": 45 if (snap["users"] or 0) >= 5 else 32,
            "networking": 36}
    for key, score in base.items():
        state = has.get(key)
        if state is True:
            continue
        why = "Not on their account" if state is False else "Not recorded in Zoho: check first"
        out.append((key, score if state is False else score - 25, why))
    out.sort(key=lambda x: -x[1])
    return out


# ==========================================
# 2. EMAIL: COPY + BRANDED HTML
# ==========================================

SENDER_DEFAULTS = {"name": "", "title": ""}


def looks_like_company_name(name: str) -> bool:
    flat = re.sub(r"[^a-z]", "", (name or "").lower())
    return bool(flat) and (flat.startswith("sycom") or flat.startswith("syplus") or flat.startswith("southwales")
                           or flat in ("sy", "sycommunications", "swcomms") or "communications" in flat
                           or flat.endswith("comms"))


def get_sender() -> Dict[str, str]:
    prof = dict(SENDER_DEFAULTS)
    prof.update({k: v for k, v in st.session_state.get("sender_profile", {}).items() if v})
    if looks_like_company_name(prof.get("name", "")):
        prof["name"] = ""
    return prof


def build_subject(key: str, company: str, prof: Dict[str, Any]) -> str:
    return {
        "renewal": f"Your phone contract review, {company}",
        "integration": f"Connect your phones to {prof['crms'][0]}, {company}",
        "call_scope": f"See every call at {company} with Call Scope",
        "mobiles": f"{company}'s mobiles and phones on one bill",
        "broadband": f"Faster, more reliable broadband for {company}",
        "cctv": f"Keep an eye on {company} from your phone",
        "headsets": f"Clearer calls for the team at {company}",
        "networking": f"Wi-Fi that reaches every corner of {company}",
    }.get(key, f"A few ideas for {company}")


def services_summary(has: Dict[str, Optional[bool]]) -> str:
    names = {"broadband": "broadband", "mobiles": "mobiles", "call_scope": "Call Scope",
             "integration": "a CRM integration", "cctv": "CCTV", "headsets": "headsets", "networking": "networking"}
    got = ["your phone system"] + [names[k] for k, v in has.items() if v is True]
    return got[0] if len(got) == 1 else ", ".join(got[:-1]) + f" and {got[-1]}"


def build_email(item: Dict[str, Any]) -> Tuple[str, str]:
    """(subject, plain-text body) for an existing customer, from the chosen offers."""
    acct, snap, brand = item["acct"], item["snap"], item["brand"]
    prof = snap["profile"]
    company = (acct.get("Account_Name") or "your business").strip()
    contact = item["contacts"][item["contact_idx"]] if item["contacts"] else {}
    first = (contact.get("First_Name") or "").strip() or "there"
    sender = get_sender()
    offers = [o for o in item["offers"] if o in OFFER_TITLES]
    extras = [o for o in offers if o != "renewal"]

    who = f"It's {sender['name']} from {brand['name']}." if sender.get("name") else f"It's {brand['name']} here."
    parts = [f"Hi {first},", f"Hope all's well at {company}. {who}"]
    if "renewal" in offers and snap.get("end"):
        if (snap.get("months_left") or 0) < 0:
            parts.append(
                f"Your contract came to the end of its term in {snap['end'].strftime('%B %Y')}, so it's due for renewal"
                " and a good time for a quick review. We can often lower costs or upgrade handsets at the same time.")
        else:
            parts.append(
                f"Your contract is due for renewal in {snap['end'].strftime('%B %Y')}. We can review it with you now,"
                " so there are no surprises, and we can often lower costs or upgrade handsets at the same time.")
    if extras:
        lead_in = (f"You already have {services_summary(snap['has'])} with us. Here "
                   + ("is something" if len(extras) == 1 else "are a few things")
                   + f" that work{'s' if len(extras) == 1 else ''} well for {prof['plural']}"
                   + " and could be worth adding:")
        parts.append(lead_in)
        parts.append("\n".join(f"- {OFFER_TITLES[o]}: {offer_line(o, prof)}" for o in extras))
    if "call_scope" in offers:
        parts.append(f"See Call Scope in 60 seconds: {_secret_value('CALLSCOPE_URL', CALLSCOPE_URL_DEFAULT)}")
    phone = brand.get("phone") or ""
    parts.append("Fancy a quick 10-minute call to talk it through? Just reply to this email"
                 + (f" or call us on {phone}." if phone else "."))
    sig = ["Kind regards,"]
    if sender.get("name"):
        sig += ["", sender["name"]] + ([sender["title"]] if sender.get("title") else [])
    sig.append(brand["name"])
    contact_line = " | ".join(x for x in (brand.get("phone"), brand.get("email")) if x)
    if contact_line:
        sig.append(contact_line)
    if brand.get("website"):
        sig.append(brand["website"])
    parts.append("\n".join(sig))
    parts.append("P.S. If you'd rather not get emails like this, just reply \"no thanks\" and we'll take you off the list.")
    subject = build_subject(offers[0] if offers else "", company, prof)
    return subject, "\n\n".join(parts)


def _email_plain_html(body: str) -> str:
    out = []
    for block in body.replace("\r\n", "\n").split("\n\n"):
        lines = [l for l in block.split("\n") if l.strip()] or [""]
        if all(l.lstrip().startswith("- ") for l in lines):
            items = "".join(f"<li>{html_lib.escape(l.lstrip()[2:])}</li>" for l in lines)
            out.append(f'<ul style="margin:0 0 14px 0;padding-left:20px">{items}</ul>')
        else:
            text = "<br>".join(html_lib.escape(l) for l in block.split("\n"))
            style = "margin:0 0 14px 0" + (";color:#6b7280;font-size:12px" if block.startswith("P.S.") else "")
            out.append(f'<p style="{style}">{text}</p>')
    return ('<html><body style="font-family:Calibri,Arial,sans-serif;font-size:14px;line-height:1.45;color:#1f2937">'
            + "".join(out) + "</body></html>")


def _email_branded_html(body: str, subject: str, brand: Dict[str, Any]) -> str:
    """Branded email (tables + inline styles, no images) in the account's own brand colours."""
    purple, teal = brand.get("primary") or "#1f1450", brand.get("accent") or "#00b5a3"
    font = "font-family:'Segoe UI',Calibri,Arial,Helvetica,sans-serif"
    e = html_lib.escape
    rows: List[str] = []
    sig_lines: List[str] = []
    ps, in_sig = "", False

    def para(text: str, extra: str = "") -> str:
        inner = "<br>".join(e(l) for l in text.split("\n"))
        return (f'<tr><td style="padding:0 36px 16px 36px;{font};font-size:15px;line-height:1.6;color:#1f2937;{extra}">'
                f"{inner}</td></tr>")

    for block in [b.strip("\n") for b in body.replace("\r\n", "\n").split("\n\n")]:
        if not block.strip():
            continue
        first = block.lstrip()
        low = first.lower()
        if first.startswith("P.S."):
            ps = block
            continue
        if in_sig or low.startswith(("kind regards", "best regards", "many thanks", "regards")):
            in_sig = True
            sig_lines += [l for l in block.split("\n") if l.strip()]
            continue
        lines = [l for l in block.split("\n") if l.strip()]
        if lines and all(l.lstrip().startswith("- ") for l in lines):
            cards = ""
            for l in lines:
                title, _, desc = l.lstrip()[2:].partition(": ")
                cards += (
                    f'<tr><td style="padding:0 0 10px 0"><table role="presentation" width="100%" cellpadding="0" '
                    f'cellspacing="0" border="0"><tr><td style="background:#f5f4fb;border-left:4px solid {teal};'
                    f'border-radius:8px;padding:14px 16px;{font}">'
                    f'<div style="font-size:15px;font-weight:700;color:{purple}">'
                    f'<span style="color:{teal}">&#10003;</span>&nbsp; {e(title)}</div>'
                    + (f'<div style="font-size:14px;line-height:1.5;color:#4b5563;margin-top:4px">{e(desc)}</div>'
                       if desc else "")
                    + "</td></tr></table></td></tr>")
            rows.append(f'<tr><td style="padding:0 36px 8px 36px"><table role="presentation" width="100%" '
                        f'cellpadding="0" cellspacing="0" border="0">{cards}</table></td></tr>')
            continue
        if "due for renewal" in low:
            rows.append(
                f'<tr><td style="padding:2px 36px 18px 36px"><table role="presentation" width="100%" cellpadding="0" '
                f'cellspacing="0" border="0"><tr><td style="background:#eefaf8;border:1px solid {teal};border-radius:8px;'
                f'padding:14px 16px;{font};font-size:14px;line-height:1.55;color:#1f2937">'
                f'<strong style="color:{purple}">&#128197; Contract review</strong><br>{e(block)}</td></tr></table></td></tr>')
            continue
        m = re.match(r"^(See Call Scope[^:]*):\s*(https?://\S+)$", first)
        if m:
            rows.append(
                f'<tr><td style="padding:0 36px 18px 36px;{font};font-size:14px">'
                f'<a href="{e(m.group(2))}" style="color:{teal};font-weight:700;text-decoration:none">'
                f'&#9654;&nbsp; {e(m.group(1))} &rarr;</a></td></tr>')
            continue
        if low.startswith(("fancy a quick", "worth a quick")):
            head, _, rest = first.partition("?")
            href = _secret_value("DEMO_BOOKING_URL") or (
                f"mailto:{brand.get('email', '')}?subject={quote('Re: ' + (subject or 'a quick call'))}")
            rows.append(
                f'<tr><td align="center" style="padding:8px 36px 6px 36px">'
                f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>'
                f'<td align="center" bgcolor="{teal}" style="border-radius:8px">'
                f'<a href="{e(href)}" style="display:inline-block;padding:13px 30px;{font};font-size:15px;font-weight:700;'
                f'color:#ffffff;text-decoration:none;border-radius:8px">Book a quick call &rarr;</a></td></tr></table></td></tr>')
            if rest.strip():
                rows.append(para(rest.strip(), "text-align:center;font-size:14px;color:#4b5563;padding-top:10px"))
            continue
        rows.append(para(block))

    sig_html = ""
    if sig_lines:
        closing, rest_lines = sig_lines[0], sig_lines[1:]
        name_lines = [l for l in rest_lines if l.strip() != brand["name"] and "|" not in l and "www." not in l
                      and "@" not in l]
        contact = next((l for l in rest_lines if "|" in l or "@" in l), "")
        site = next((l for l in rest_lines if "www." in l), "")
        who = "".join(
            f'<div style="{font};font-size:{15 if i == 0 else 13}px;font-weight:{700 if i == 0 else 400};'
            f'color:{purple if i == 0 else "#4b5563"}">{e(l)}</div>' for i, l in enumerate(name_lines))
        site_html = (f'<a href="https://{e(site.strip().replace("https://", "").replace("http://", ""))}" '
                     f'style="color:{teal};text-decoration:none;font-weight:600">{e(site.strip())}</a>' if site else "")
        sig_html = (
            f'<tr><td style="padding:10px 36px 26px 36px">'
            f'<div style="{font};font-size:15px;color:#1f2937;margin-bottom:12px">{e(closing)}</div>'
            f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td style="border-left:3px solid {teal};padding:2px 0 2px 14px">{who}'
            f'<div style="{font};font-size:14px;font-weight:700;color:{purple};margin-top:{4 if who else 0}px">{e(brand["name"])}</div>'
            f'<div style="{font};font-size:13px;color:#4b5563;margin-top:2px">{e(contact)}</div>'
            f'<div style="{font};font-size:13px;margin-top:2px">{site_html}</div>'
            f"</td></tr></table></td></tr>")
    header = (
        f'<tr><td bgcolor="{purple}" style="background:{purple};padding:22px 36px;border-radius:12px 12px 0 0">'
        f'<div style="{font};font-size:20px;font-weight:800;color:#ffffff;letter-spacing:.2px">'
        f'{e(brand.get("word1") or "")} <span style="color:{teal}">{e(brand.get("word2") or "")}</span></div>'
        f'<div style="{font};font-size:12px;color:#d6d3ea;margin-top:3px">{e(brand.get("tagline") or "")}</div>'
        f'</td></tr>'
        f'<tr><td height="4" bgcolor="{teal}" style="background:{teal};font-size:0;line-height:0">&nbsp;</td></tr>'
        f'<tr><td style="padding:28px 0 0 0;font-size:0;line-height:0">&nbsp;</td></tr>')
    footer = (f'<tr><td style="padding:14px 36px 0 36px;{font};font-size:12px;line-height:1.5;color:#8a8fa3">{e(ps)}</td></tr>'
              if ps else "")
    address = brand.get("address") or ""
    return (
        '<html><body style="margin:0;padding:0;background:#f1f0f7">'
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f1f0f7" '
        'style="background:#f1f0f7"><tr><td align="center" style="padding:24px 12px">'
        '<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px">'
        '<tr><td><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" '
        f'style="background:#ffffff;border-radius:12px;border:1px solid #e4e1f0">{header}{"".join(rows)}{sig_html}</table></td></tr>'
        f"{footer}"
        + (f'<tr><td style="padding:6px 36px 0 36px;{font};font-size:11px;color:#a3a7b8">{e(brand["name"])} · {e(address)}</td></tr>'
           if address else "")
        + "</table></td></tr></table></body></html>")


def email_html(body: str, subject: str, brand: Dict[str, Any]) -> str:
    return _email_branded_html(body, subject, brand) if st.session_state.get("opt_branded", True) else _email_plain_html(body)


# ==========================================
# 3. STREAMLIT APPLICATION
# ==========================================

st.set_page_config(page_title=f"{APP_NAME} · Existing customers", page_icon="🎯", layout="wide")
inject_css()
hero_slot = st.empty()

ZOHO = ZohoCRM()
SENT_LOG = SentLog("GITHUB_CG_LOG_PATH", "cg_sent_log.json", ".cg_sent_log.json")
SETTINGS = SentLog("GITHUB_CG_SETTINGS_PATH", "cg_settings.json", ".cg_settings.json")
ACCOUNT_BASE = ["Account_Name", "Account_Type", "Industry", "Phone", "Website", "Billing_City", "Billing_Code",
                "Created_Time"]
CONTACT_FIELDS = ["First_Name", "Last_Name", "Email", "Title", "Email_Opt_Out", "Account_Name"]
# Field types COQL can't select; these are fetched with the Get Records API instead
COQL_UNSUPPORTED = {"fileupload", "imageupload", "subform", "multiselectlookup", "profileimage",
                    "multi_module_lookup", "multiuserlookup"}


PICK_TYPES = {"picklist", "multiselectpicklist"}


def detect_type_field(afields: Dict[str, Dict[str, Any]]) -> str:
    """The Account field that holds SYC Customer / SY Plus Customer / South Wales Comms."""
    saved = get_settings().get("type_field")
    if saved and saved in afields:
        return saved
    # Zoho's own Account Type field wins whenever it holds the customer types
    if any(brand_key(v) for v in ZOHO.picklist(afields, "Account_Type")):
        return "Account_Type"
    best, best_n = "Account_Type", 0
    for api, f in afields.items():
        if (f.get("data_type") or "") not in PICK_TYPES:
            continue
        n = sum(1 for v in ZOHO.picklist(afields, api) if brand_key(v))
        if n > best_n or (n == best_n and n and api == "Account_Type"):
            best, best_n = api, n
    return best


def type_matches(value: Any, wanted: Set[str]) -> bool:
    vals = value if isinstance(value, list) else [value]
    return any(value_text(v) in wanted for v in vals)


def load_accounts(types: List[str], afields: Dict[str, Dict[str, Any]], fmap: Dict[str, str]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Fast path is COQL. If Zoho refuses the query for any reason, fall back to reading every account with the
    Get Records API (slower, but it accepts any field) and filter by type here."""
    tf = detect_type_field(afields)
    aliases = ZOHO.picklist_aliases(afields, tf)
    # Every spelling of the chosen types (e.g. 'SYC Customer' is stored as 'Customer' if it was renamed in Zoho)
    wanted = set(types) | {a for a, shown in aliases.items() if shown in types}
    try:
        if (afields.get(tf, {}).get("data_type") or "") == "multiselectpicklist":
            raise ZohoError("the customer type field is a multi-select list")
        accts, skipped = _load_accounts_coql(sorted(wanted), afields, fmap, tf)
    except ZohoError as exc:
        st.session_state["load_diag"] = f"COQL refused the query ({exc}); used the slower Get Records route instead."
        base = [f for f in ACCOUNT_BASE if f in afields]
        mapped = [v for v in dict.fromkeys(list(fmap.values()) + [tf]) if v in afields and v not in base]
        recs = ZOHO.get_records("Accounts", (base + mapped)[:50])
        accts, skipped = [r for r in recs.values() if type_matches(r.get(tf), wanted)], []
    for a in accts:
        vals = [aliases.get(value_text(v), value_text(v)) for v in (a.get(tf) if isinstance(a.get(tf), list) else [a.get(tf)])]
        a["_type"] = next((v for v in vals if v in types), vals[0] if vals else "")
    return accts, skipped


def load_contacts() -> List[Dict[str, Any]]:
    try:
        return ZOHO.query_all("Contacts", CONTACT_FIELDS, "Email is not null")
    except ZohoError:
        recs = ZOHO.get_records("Contacts", CONTACT_FIELDS)
        return [r for r in recs.values() if (r.get("Email") or "").strip()]


def _load_accounts_coql(types: List[str], afields: Dict[str, Dict[str, Any]], fmap: Dict[str, str],
                        tf: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Accounts of the given types with every mapped field. Returns (accounts, labels of fields skipped)."""
    base = [f for f in ACCOUNT_BASE if f in afields]
    mapped = [v for v in dict.fromkeys(list(fmap.values()) + [tf]) if v in afields and v not in base]
    by_api = [f for f in mapped if (afields[f].get("data_type") or "") in COQL_UNSUPPORTED]
    extra = [f for f in mapped if f not in by_api]
    quoted = ", ".join("'" + t.replace("'", "\\'") + "'" for t in types)
    where = f"{tf} in ({quoted})"
    skipped: List[str] = []
    try:
        accts = ZOHO.query_all("Accounts", base + extra, where)
    except ZohoError as exc:
        if "invalid" not in str(exc).lower():
            raise
        # Find the column(s) Zoho won't accept, drop them and carry on
        good = []
        for f in extra:
            try:
                ZOHO._request("POST", "/crm/v8/coql", json={"select_query":
                              f"select Account_Name, {f} from Accounts where {where} limit 0, 1"})
                good.append(f)
            except ZohoError:
                by_api.append(f)
        accts = ZOHO.query_all("Accounts", base + good, where)
    if by_api:
        try:
            extra_vals = ZOHO.get_records("Accounts", ["Account_Name"] + by_api)
            for a in accts:
                rec = extra_vals.get(str(a.get("id")), {})
                for f in by_api:
                    a[f] = rec.get(f)
        except ZohoError:
            skipped += [afields[f].get("field_label") or f for f in by_api]
    return accts, skipped
DECISION_WORDS = ("owner", "director", "partner", "principal", "managing", "ceo", "founder", "proprietor")
MANAGER_WORDS = ("manager", "head", "lead")
MAX_BATCH = 25
NOT_MAPPED = "— not in Zoho —"

for _k, _v in {"opt_branded": True, "queue_ver": 0, "sent_log_ver": 0}.items():
    st.session_state.setdefault(_k, _v)
st.session_state.setdefault("queue", {})
st.session_state.setdefault("queue_order", [])


def columns(spec, **kwargs):
    try:
        return st.columns(spec, vertical_alignment="bottom", **kwargs)
    except TypeError:
        return st.columns(spec, **kwargs)


def _data_editor(df: pd.DataFrame, **kwargs):
    try:
        return st.data_editor(df, width="stretch", **kwargs)
    except Exception:
        return st.data_editor(df, use_container_width=True, **kwargs)


def _dataframe(df: pd.DataFrame, **kwargs):
    try:
        return st.dataframe(df, width="stretch", **kwargs)
    except Exception:
        return st.dataframe(df, use_container_width=True, **kwargs)


def bump() -> None:
    st.session_state["queue_ver"] = st.session_state.get("queue_ver", 0) + 1


# ---------- shared stores ----------
def get_sent_log() -> Dict[str, Any]:
    if "sent_log_data" not in st.session_state:
        st.session_state["sent_log_data"] = SENT_LOG.load()
    return st.session_state["sent_log_data"]


def record_sent(changes: Dict[str, Optional[Dict[str, Any]]]) -> None:
    local = dict(get_sent_log())
    try:
        st.session_state["sent_log_data"] = SENT_LOG.apply(changes, f"Customer Growth: {len(changes)} updated")
    except Exception as exc:
        for key, rec in changes.items():
            if rec is None:
                local.pop(key, None)
            else:
                local[key] = rec
        st.session_state["sent_log_data"] = local
        st.session_state["sent_log_error"] = str(exc) if isinstance(exc, RuntimeError) else "Couldn't save the log."
    st.session_state["sent_log_ver"] = st.session_state.get("sent_log_ver", 0) + 1
    bump()


def get_settings() -> Dict[str, Any]:
    if "settings_data" not in st.session_state:
        st.session_state["settings_data"] = SETTINGS.load()
    return st.session_state["settings_data"]


def save_settings(key: str, value: Any) -> Optional[str]:
    try:
        st.session_state["settings_data"] = SETTINGS.apply({key: value}, f"Customer Growth: {key} updated")
        return None
    except Exception as exc:
        st.session_state.setdefault("settings_data", {})[key] = value
        return str(exc)


def get_brands() -> Dict[str, Dict[str, Any]]:
    saved = get_settings().get("brands") or {}
    out = {}
    for t, d in DEFAULT_BRANDS.items():
        out[t] = dict(d, **{k: v for k, v in (saved.get(t) or {}).items() if v not in (None,)})
    for t, d in saved.items():
        if t not in out:
            out[t] = dict(DEFAULT_BRANDS["SYC Customer"], **d)
    return out


def brand_for(account_type: str) -> Tuple[Dict[str, Any], bool]:
    """(brand, is_fallback). Brands without an email and phone fall back to SY Communications."""
    brands = get_brands()
    b = brands.get(account_type or "") or brands.get(brand_key(account_type or "") or "")
    if b and b.get("email") and b.get("phone"):
        return b, False
    return brands["SYC Customer"], (brand_key(account_type or "") or account_type) != "SYC Customer"


def get_field_map() -> Tuple[Dict[str, str], bool]:
    """(map, saved). Uses the saved mapping, else a best guess from the Account field labels."""
    saved = get_settings().get("field_map")
    if isinstance(saved, dict) and saved:
        out = {k: v for k, v in saved.items() if v}
        if "contract_term" not in saved:  # Added after some mappings were saved: fill it in automatically
            auto = auto_field_map(st.session_state.get("acct_fields") or {})
            if auto.get("contract_term"):
                out["contract_term"] = auto["contract_term"]
        return out, True
    return auto_field_map(st.session_state.get("acct_fields") or {}), False


def load_meta() -> Optional[str]:
    if "acct_fields" in st.session_state:
        return None
    try:
        st.session_state["acct_fields"] = ZOHO.fields("Accounts")
    except ZohoError as exc:
        return str(exc)
    st.session_state["zoho_org_domain"] = ZOHO.org_domain()
    return None


def zoho_senders() -> Tuple[List[Dict[str, Any]], Optional[str]]:
    if "zoho_from" not in st.session_state:
        try:
            st.session_state["zoho_from"] = ZOHO.from_addresses()
        except ZohoError as exc:
            return [], str(exc)
    return st.session_state["zoho_from"], None


def contact_name(c: Dict[str, Any]) -> str:
    return " ".join(x for x in [(c.get("First_Name") or "").strip(), (c.get("Last_Name") or "").strip()] if x)


def rank_contacts(contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    def score(c: Dict[str, Any]) -> Tuple[int, int]:
        title = (c.get("Title") or "").lower()
        tier = 0 if any(w in title for w in DECISION_WORDS) else 1 if any(w in title for w in MANAGER_WORDS) else 2
        return (1 if c.get("Email_Opt_Out") else 0, tier)
    return sorted(contacts, key=score)


def build_item(acct: Dict[str, Any]) -> Dict[str, Any]:
    fmap, _ = get_field_map()
    snap = account_snapshot(acct, fmap)
    brand, fallback = brand_for(acct.get("_type") or "")
    contacts = rank_contacts(st.session_state.get("contacts_by_acct", {}).get(acct["id"], []))
    ranked = rank_offers(snap)
    return {
        "acct": acct, "snap": snap, "brand": brand, "brand_fallback": fallback, "contacts": contacts,
        "contact_idx": 0, "ranked": ranked, "offers": [k for k, _, _ in ranked[:3]],
        "include": True, "subject": None, "body": None, "sig": None,
    }


def current_contact(item: Dict[str, Any]) -> Dict[str, Any]:
    return item["contacts"][item["contact_idx"]] if item["contacts"] else {}


def item_email(item: Dict[str, Any]) -> str:
    c = current_contact(item)
    return "" if (not c or c.get("Email_Opt_Out")) else (c.get("Email") or "").strip()


def ensure_draft(item: Dict[str, Any]) -> None:
    sig = (tuple(item["offers"]), item["contact_idx"], tuple(sorted(get_sender().items())), item["brand"]["name"])
    if item.get("sig") != sig or item.get("body") is None:
        item["subject"], item["body"] = build_email(item)
        item["sig"] = sig


def add_to_queue(accts: List[Dict[str, Any]]) -> None:
    q, order = st.session_state["queue"], st.session_state["queue_order"]
    for a in accts:
        q[a["id"]] = build_item(a)
        if a["id"] not in order:
            order.append(a["id"])
    if accts:
        st.session_state["current_id"] = accts[0]["id"]
        st.session_state["current_id_select"] = accts[0]["id"]
    bump()


def sent_record(item: Dict[str, Any], via: str = "") -> Dict[str, Any]:
    c = current_contact(item)
    return {
        "company_name": item["acct"].get("Account_Name", ""), "to": item_email(item), "contact": contact_name(c),
        "brand": item["brand"]["name"], "offers": [OFFER_TITLES.get(o, o) for o in item["offers"]],
        "subject": item.get("subject") or "", "sent_at": now_uk().isoformat(timespec="seconds"),
        "sent_by": get_sender().get("name", ""), "status": "Emailed via Zoho" if via == "zoho" else "Handled",
        "via": via,
    }


def zoho_sent_today(log: Dict[str, Any]) -> int:
    today = now_uk().date().isoformat()
    return sum(1 for r in log.values() if r.get("via") == "zoho" and str(r.get("sent_at", "")).startswith(today))


def pick_from(senders: List[Dict[str, Any]], brand: Dict[str, Any], default_idx: int) -> Optional[Dict[str, Any]]:
    """The Zoho From address matching the brand's email, else the one chosen in the panel."""
    for s_ in senders:
        if s_.get("email", "").lower() == (brand.get("email") or "").lower():
            return s_
    return senders[default_idx] if senders and 0 <= default_idx < len(senders) else (senders[0] if senders else None)


def push_to_zoho(ids: List[str], default_from_idx: int, origin: str = "panel") -> None:
    queue = st.session_state["queue"]
    senders, _ = zoho_senders()
    done, problems = [], []
    changes: Dict[str, Optional[Dict[str, Any]]] = {}
    who = get_sender().get("name") or "Customer Growth"
    stamp = now_uk().strftime("%d %b %Y %H:%M")
    progress = st.progress(0.0, text="Talking to Zoho…")
    for n, aid in enumerate(ids, start=1):
        item = queue.get(aid)
        if not item:
            continue
        name = item["acct"].get("Account_Name", "customer")
        progress.progress(n / len(ids), text=f"Sending {n} of {len(ids)} · {name}")
        ensure_draft(item)
        c, to = current_contact(item), item_email(item)
        if not to or not c.get("id"):
            problems.append(f"{name}: no contact email (or the contact opted out)")
            continue
        if not item["offers"]:
            problems.append(f"{name}: no ideas picked, so nothing to send")
            continue
        sender = pick_from(senders, item["brand"], default_from_idx)
        if not sender:
            problems.append(f"{name}: no From address available in Zoho")
            continue
        try:
            ZOHO.send_mail("Contacts", str(c["id"]), sender, to, contact_name(c), item["subject"],
                           email_html(item["body"], item["subject"], item["brand"]))
        except ZohoError as exc:
            problems.append(f"{name}: not sent. {exc}")
            continue
        note = (f"Emailed {contact_name(c) or to} ({to}) via Customer Growth on {stamp}, by {who}.\n"
                f"Brand: {item['brand']['name']} (from {sender.get('email')})\nSubject: {item['subject']}\n"
                f"Ideas: {', '.join(OFFER_TITLES.get(o, o) for o in item['offers'])}")
        try:
            ZOHO.add_note("Accounts", aid, "Customer Growth: email sent", note)
        except ZohoError as exc:
            problems.append(f"{name}: sent, but the note wasn't added. {exc}")
        changes[aid] = dict(sent_record(item, via="zoho"), from_address=sender.get("email", ""))
        done.append(name)
    progress.empty()
    if changes:
        record_sent(changes)
    st.session_state["push_result"] = {"done": done, "problems": problems, "origin": origin}


def show_push_result(origin: str) -> None:
    res = st.session_state.get("push_result")
    if not res or res.get("origin") != origin:
        return
    st.session_state.pop("push_result", None)
    if res["done"]:
        st.success(f"{len(res['done'])} sent via Zoho: " + ", ".join(res["done"][:6]) + ("…" if len(res["done"]) > 6 else ""))
    for p in res["problems"]:
        st.warning(p)


def render_zoho_setup() -> None:
    render_html(
        '<div class="pe-panel"><div class="h">One-off Zoho setup</div>'
        '<div style="font-size:.86rem;line-height:1.55;color:var(--muted)">'
        "<b>1.</b> In <b>api-console.zoho.eu</b>, open your Self Client and go to <b>Generate Code</b>.<br>"
        "<b>2.</b> Paste the scope below, pick <b>10 minutes</b>, add any description and click <b>Create</b>.<br>"
        "<b>3.</b> Copy the code it shows (starts <b>1000.</b>), paste it here and click Connect. Be quick: codes expire.</div></div>"
    )
    st.code(ZOHO_SCOPE, language=None)
    with st.form("zoho_setup", border=False):
        zc1, zc2 = columns([2.2, 1])
        with zc1:
            setup_code = st.text_input("Code from Zoho", type="password", placeholder="1000.xxxxxxxx…")
        with zc2:
            setup_go = st.form_submit_button("Connect Zoho", type="primary", **FULL_WIDTH)
    if setup_go:
        if not setup_code.strip():
            st.warning("Paste the code from Zoho first.")
        else:
            with st.spinner("Asking Zoho for a permanent key…"):
                st.session_state["zoho_setup_result"] = ZOHO.exchange_code(setup_code)
    result = st.session_state.get("zoho_setup_result") or {}
    if result.get("error"):
        st.error(result["error"])
    elif result.get("refresh_token"):
        st.success("Connected. Zoho gave us a permanent key. Last step:")
        st.code(f'ZOHO_REFRESH_TOKEN = "{result["refresh_token"]}"', language=None)
        st.caption("Copy that whole line into this app's Streamlit Secrets, save, then reboot the app."
                   " The key is shown only on this screen, so don't share it in emails or chats.")


def fmt_date(d: Optional[datetime]) -> str:
    return d.strftime("%d %b %Y").lstrip("0") if d else "—"


# ---------------- Sidebar ----------------
with st.sidebar:
    render_html(
        f'<div class="pe-brand"><div class="pe-logo">{icon("target", 22, 2.2)}</div>'
        f'<div><div class="n">{APP_NAME}</div><div class="s">{APP_TAGLINE}</div></div></div>'
    )
    render_html('<div class="pe-side-h">Connections</div>')
    zoho_state = ('idle">Setup needed' if ZOHO.can_setup else 'off">Not set up' if not ZOHO.configured
                  else 'ok">Connected' if st.session_state.get("acct_fields") else 'idle">Ready')
    get_sent_log()
    set_state = 'ok">Saved to GitHub' if SETTINGS.backend == "github" else 'idle">Temporary'
    log_state = ('off">Error' if (SENT_LOG.last_error or st.session_state.get("sent_log_error"))
                 else 'ok">Saved to GitHub' if SENT_LOG.backend == "github" else 'idle">Temporary')
    render_html(
        f'<div class="pe-status">Zoho CRM<span class="st {zoho_state}</span></div>'
        f'<div class="pe-status">Sent log<span class="st {log_state}</span></div>'
        f'<div class="pe-status">Settings<span class="st {set_state}</span></div>'
    )
    if SENT_LOG.last_error or st.session_state.get("sent_log_error"):
        st.caption("⚠️ " + (st.session_state.pop("sent_log_error", None) or SENT_LOG.last_error or ""))
    if st.button("↻ Refresh shared data", **FULL_WIDTH, help="Pick up colleagues' sends and settings."):
        for k in ("sent_log_data", "settings_data", "zoho_from", "acct_fields"):
            st.session_state.pop(k, None)
        bump()
        st.rerun()
    render_html('<div class="pe-side-h">This session</div>')
    sidebar_stats_slot = st.empty()
    render_html('<div class="pe-side-h">You</div>')
    with st.expander("Your name (optional)", expanded=False):
        prof = st.session_state.setdefault("sender_profile", {"name": "", "title": ""})
        prof["name"] = st.text_input("Your name", value=prof.get("name", ""), placeholder="Leave blank to sign as the brand")
        prof["title"] = st.text_input("Job title", value=prof.get("title", ""), placeholder="e.g. Account Manager")
        st.session_state["sender_profile"] = prof
        st.caption("Blank: emails open \"It's SY Communications here\" (or the customer's brand) and are signed by the brand.")
    render_html('<div class="pe-side-h">Account</div>')
    if st.button("Log out", **FULL_WIDTH):
        st.session_state["password_correct"] = False
        st.rerun()

col_left, col_right = st.columns([1.08, 0.92], gap="large")
queue: Dict[str, Dict[str, Any]] = st.session_state["queue"]

# ---------------- Left: load + pick ----------------
with col_left:
    with st.container(key="card-left"):
        section_header("01", "Customers", "Pull your existing accounts from Zoho by account type.")
        ready = False
        if ZOHO.can_setup:
            render_zoho_setup()
        elif not ZOHO.configured:
            render_html(
                f'<div class="pe-hint">{icon("pointer", 16)}<div>Zoho CRM isn\'t connected yet. Add '
                "<b>ZOHO_CLIENT_ID</b> and <b>ZOHO_CLIENT_SECRET</b> to Streamlit Secrets and reboot."
                " A one-off setup box will then appear here.</div></div>")
        else:
            err = load_meta()
            if err and ("invalid_code" in err or "permission" in err.lower()):
                st.error("Zoho needs a (new) key for this app. Get one below, then put it in Secrets as ZOHO_REFRESH_TOKEN.")
                render_zoho_setup()
            elif err:
                st.error(err)
                if st.button("Try again", key="zoho_retry"):
                    st.session_state.pop("zoho_token", None)
                    st.rerun()
            else:
                ready = True

        if ready:
            afields = st.session_state["acct_fields"]
            tf = detect_type_field(afields)
            types = ZOHO.picklist(afields, tf) or ACCOUNT_TYPES_DEFAULT
            default_types = ([t for t in types if brand_key(t) == "SYC Customer"]
                             or [t for t in types if brand_key(t)] or types[:1])
            if not any(brand_key(t) for t in types):
                st.warning(f"The '{afields.get(tf, {}).get('field_label', tf)}' field has no SYC / SY Plus / South Wales"
                           " options. Pick the field that holds your customer types:")
            pick_fields = [a_ for a_, f_ in afields.items() if (f_.get("data_type") or "") in PICK_TYPES]
            with st.expander("Customer type field", expanded=not any(brand_key(t) for t in types)):
                new_tf = st.selectbox(
                    "Which Account field says SYC Customer / SY Plus Customer / South Wales Comms?", pick_fields,
                    index=pick_fields.index(tf) if tf in pick_fields else 0,
                    format_func=lambda a_: f"{afields[a_].get('field_label') or a_}  ·  "
                                           + ", ".join(ZOHO.picklist(afields, a_)[:6]),
                    key="type_field_pick")
                if new_tf != tf and st.button("Use this field", type="primary"):
                    save_settings("type_field", new_tf)
                    st.session_state.pop("accts", None)
                    st.rerun()
            t1, t2 = columns([2.2, 1])
            with t1:
                chosen_types = st.multiselect("Account type", types, default=default_types,
                                              help="Which customers to load. Your three customer types are ticked.")
            with t2:
                load_btn = st.button("Load customers", type="primary", disabled=not chosen_types, **FULL_WIDTH)
            fmap, fmap_saved = get_field_map()
            if load_btn:
                skipped_fields: List[str] = []
                with st.spinner("Pulling accounts and contacts from Zoho…"):
                    try:
                        accts, skipped_fields = load_accounts(chosen_types, afields, fmap)
                        load_err = None
                    except ZohoError as exc:
                        accts, load_err = [], f"Couldn't load accounts. {exc}"
                    contacts: List[Dict[str, Any]] = []
                    if not load_err:
                        try:
                            contacts = load_contacts()
                        except ZohoError as exc:
                            load_err = f"Loaded the accounts but not their contacts. {exc}"
                if st.session_state.get("load_diag"):
                    with st.expander("Technical details"):
                        st.caption(st.session_state.pop("load_diag"))
                if skipped_fields:
                    st.warning("Zoho wouldn't let the app read: " + ", ".join(skipped_fields)
                               + ". Those services show as 'not recorded'. Pick a different field in the mapping if you can.")
                if load_err and not accts:
                    st.error(load_err)
                else:
                    if load_err:
                        st.warning(load_err)
                    by_acct: Dict[str, List[Dict[str, Any]]] = {}
                    for c in contacts:
                        aid = str((c.get("Account_Name") or {}).get("id") or "") if isinstance(c.get("Account_Name"), dict) else ""
                        if aid:
                            by_acct.setdefault(aid, []).append(c)
                    for a in accts:
                        a["id"] = str(a.get("id"))
                        a["_snap"] = account_snapshot(a, fmap)
                        a["_ranked"] = rank_offers(a["_snap"])
                    st.session_state["contacts_by_acct"] = by_acct
                    st.session_state["accts"] = accts
                    st.session_state["table_ver"] = st.session_state.get("table_ver", 0) + 1
                    if not accts:
                        st.warning("No accounts with those types.")

            accts_all = st.session_state.get("accts") or []
            if accts_all:
                cba = st.session_state.get("contacts_by_acct", {})
                with_email = sum(1 for a in accts_all if any(not c.get("Email_Opt_Out") for c in cba.get(a["id"], [])))
                renewing = sum(1 for a in accts_all if a["_snap"]["months_left"] is not None and 0 <= a["_snap"]["months_left"] <= 12)
                render_html(
                    '<div class="pe-stats" style="margin-top:6px">'
                    f'<div class="pe-stat"><div class="v">{len(accts_all):,}</div><div class="l">Customers</div></div>'
                    f'<div class="pe-stat"><div class="v">{with_email:,}</div><div class="l">With a contact email</div></div>'
                    f'<div class="pe-stat"><div class="v">{renewing:,}</div><div class="l">Renewing ≤ 12 months</div></div>'
                    "</div>")

            # ---- Field mapping (once, shared) ----
            with st.expander("⚙️  Zoho field mapping" + ("" if fmap_saved else "  ·  using SY Comms defaults"), expanded=False):
                st.caption("Tell the app which Account fields hold each service and the contract dates. I've guessed from"
                           " the field names; fix any that are wrong, then Save. It's saved for everyone.")
                opts = [NOT_MAPPED] + sorted(afields, key=lambda k: (afields[k].get("field_label") or k).lower())

                def _flabel(api: str) -> str:
                    if api == NOT_MAPPED:
                        return api
                    f = afields.get(api, {})
                    return f"{f.get('field_label') or api}  ({f.get('data_type', '')})"

                with st.form("field_map_form", border=False):
                    new_map: Dict[str, str] = {}
                    mcols = st.columns(2)
                    for i, (slot, label, _, kind) in enumerate(MAP_SLOTS):
                        cur = fmap.get(slot, NOT_MAPPED)
                        with mcols[i % 2]:
                            pick = st.selectbox(label, opts, index=opts.index(cur) if cur in opts else 0,
                                                format_func=_flabel, key=f"map_{slot}")
                        if pick != NOT_MAPPED:
                            new_map[slot] = pick
                    if st.form_submit_button("Save mapping", type="primary"):
                        e_ = save_settings("field_map", new_map)
                        st.session_state.pop("accts", None)
                        (st.warning(f"Saved for this session only: {e_}") if e_ else
                         st.success("Saved. Click Load customers again to use it."))
                if "contract_end" not in fmap:
                    st.caption("💡 Without a contract end date, the renewal filters and contract-review emails are switched off.")
                if fmap_saved and st.button("↺ Reset to the SY Comms defaults", key="map_reset"):
                    save_settings("field_map", {})
                    for slot, _, _, _ in MAP_SLOTS:
                        st.session_state.pop(f"map_{slot}", None)
                    st.session_state.pop("accts", None)
                    st.rerun()
                prod_api = fmap.get("services")
                prod_vals = ZOHO.picklist(afields, prod_api) if prod_api else []
                if prod_vals:
                    def _svc_of(v: str) -> str:
                        low = v.lower()
                        hits = [OFFER_TITLES[k] for k, ws in SERVICE_WORDS.items() if any(w in low for w in ws)]
                        return ", ".join(hits) if hits else "—"
                    st.caption(f"How each **{afields.get(prod_api, {}).get('field_label', 'product')}** option is read"
                               " (— means it doesn't count towards any idea):")
                    _dataframe(pd.DataFrame([{"Option in Zoho": v, "Counts as": _svc_of(v)} for v in prod_vals]),
                               hide_index=True, height=min(38 + 35 * len(prod_vals), 320))

            # ---- Brand details (once, shared) ----
            brands = get_brands()
            missing = [t for t in ACCOUNT_TYPES_DEFAULT if not (brands[t].get("email") and brands[t].get("phone"))]
            with st.expander("🎨  Brand details" + (f"  ·  {len(missing)} to fill in" if missing else ""), expanded=False):
                st.caption("Each account type is emailed as its own brand. Until a brand has an email and phone number,"
                           " its customers get SY Communications emails.")
                btype = st.selectbox("Brand for account type", list(brands.keys()), key="brand_pick")
                b = brands[btype]
                with st.form(f"brand_form_{btype}", border=False):
                    vals: Dict[str, str] = {}
                    bc = st.columns(2)
                    for i, (k, label) in enumerate(BRAND_FIELDS):
                        with bc[i % 2]:
                            if k in ("primary", "accent"):
                                vals[k] = st.color_picker(label, value=b.get(k) or "#1f1450", key=f"b_{btype}_{k}")
                            else:
                                vals[k] = st.text_input(label, value=b.get(k) or "", key=f"b_{btype}_{k}")
                    if st.form_submit_button("Save brand", type="primary"):
                        saved_b = dict(get_settings().get("brands") or {})
                        saved_b[btype] = vals
                        e_ = save_settings("brands", saved_b)
                        for it in queue.values():  # Re-brand anything already queued
                            it["brand"], it["brand_fallback"] = brand_for(it["acct"].get("_type") or "")
                            it["sig"] = None
                        (st.warning(f"Saved for this session only: {e_}") if e_ else st.success(f"{vals['name']} saved."))

    accts_all = st.session_state.get("accts") or []
    if accts_all:
        with st.container(key="card-select"):
            log_now = get_sent_log()
            cba = st.session_state.get("contacts_by_acct", {})
            section_header("02", "Pick customers", f"{len(accts_all):,} accounts loaded · filter, then add to review")
            type_counts: Dict[str, int] = {}
            sector_counts: Dict[str, int] = {}
            for a in accts_all:
                type_counts[a.get("_type") or "—"] = type_counts.get(a.get("_type") or "—", 0) + 1
                s_ = a["_snap"]["profile"]["name"]
                sector_counts[s_] = sector_counts.get(s_, 0) + 1
            f1, f2 = st.columns(2)
            with f1:
                f_types = st.multiselect("Account type ", sorted(type_counts), placeholder="All types",
                                         format_func=lambda t: f"{t} ({type_counts[t]})")
            with f2:
                f_sectors = st.multiselect("Industry", sorted(sector_counts, key=lambda x: -sector_counts[x]),
                                           placeholder="All industries", format_func=lambda s_: f"{s_} ({sector_counts[s_]})",
                                           help="From the Industry field in Zoho.")
            has_end = any(a["_snap"]["end"] for a in accts_all)
            g1, g2, g3 = st.columns(3)
            with g1:
                f_end = st.selectbox("Contract ends", ["Any time", "In the next 3 months", "In the next 6 months",
                                                       "In the next 12 months", "In 12–24 months",
                                                       "More than 24 months away", "Already ended", "No end date in Zoho"],
                                     disabled=not has_end,
                                     help="Needs the contract end date mapped (Zoho field mapping above).")
            with g2:
                f_min_in = st.selectbox("Customer for at least", ["Any", "3 months", "6 months", "1 year", "2 years"],
                                        index=2, help="Skip brand-new customers. Uses the contract start date if mapped,"
                                                      " otherwise when the account was created in Zoho.")
            with g3:
                f_cool = st.selectbox("Hide if emailed in the last", ["30 days", "60 days", "90 days", "6 months",
                                                                     "Don't hide"], index=2)
            h1, h2 = st.columns([1.3, 1])
            with h1:
                f_missing = st.multiselect("Only customers without", [k for k in OFFER_ORDER if k != "renewal"],
                                           format_func=lambda k: OFFER_TITLES[k], placeholder="Any gap",
                                           help="e.g. pick Mobiles to find everyone who doesn't have mobiles with you.")
            with h2:
                q = st.text_input("Search", placeholder="Customer name or town").strip().lower()

            min_in = {"Any": None, "3 months": 3, "6 months": 6, "1 year": 12, "2 years": 24}[f_min_in]
            cool_days = {"30 days": 30, "60 days": 60, "90 days": 90, "6 months": 182, "Don't hide": None}[f_cool]

            def _recent(aid: str) -> bool:
                rec = log_now.get(aid)
                if not rec or cool_days is None:
                    return False
                try:
                    return (now_uk() - datetime.fromisoformat(rec["sent_at"])).days < cool_days
                except (KeyError, ValueError):
                    return False

            def _end_ok(snap: Dict[str, Any]) -> bool:
                ml = snap["months_left"]
                if f_end == "Any time":
                    return True
                if f_end == "No end date in Zoho":
                    return ml is None
                if ml is None:
                    return False
                return {"In the next 3 months": 0 <= ml <= 3, "In the next 6 months": 0 <= ml <= 6,
                        "In the next 12 months": 0 <= ml <= 12, "In 12–24 months": 12 < ml <= 24,
                        "More than 24 months away": ml > 24, "Already ended": ml < 0}[f_end]

            rows = [
                a for a in accts_all
                if (not f_types or (a.get("_type") or "—") in f_types)
                and (not f_sectors or a["_snap"]["profile"]["name"] in f_sectors)
                and _end_ok(a["_snap"])
                and (min_in is None or a["_snap"]["months_in"] is None or a["_snap"]["months_in"] >= min_in)
                and not _recent(a["id"])
                and all(a["_snap"]["has"].get(k) is not True for k in f_missing)
                and (not q or q in f"{a.get('Account_Name', '')} {a.get('Billing_City', '')}".lower())
            ]
            rows.sort(key=lambda a: (a["_snap"]["months_left"] if a["_snap"]["months_left"] is not None else 999))
            if not rows:
                st.caption("No customers match these filters.")
            else:
                def _contact_label(a: Dict[str, Any]) -> str:
                    cs = rank_contacts(cba.get(a["id"], []))
                    return contact_name(cs[0]) if cs and not cs[0].get("Email_Opt_Out") else ""

                df = pd.DataFrame([{
                    "Customer": a.get("Account_Name", ""),
                    "Type": a.get("_type", ""),
                    "Industry": a["_snap"]["profile"]["name"],
                    "Ends": a["_snap"]["end"],
                    "Left": (round(a["_snap"]["months_left"]) if a["_snap"]["months_left"] is not None else None),
                    "Ideas": ", ".join(OFFER_TITLES[k] for k, _, _ in a["_ranked"][:3]),
                    "Contact": _contact_label(a),
                    "Worked": sent_label(log_now.get(a["id"])),
                    "Zoho": ZOHO.record_url("Accounts", a["id"]),
                } for a in rows])
                sel_ver = f"{st.session_state.get('table_ver', 0)}_{abs(hash((tuple(f_types), tuple(f_sectors), f_end, f_min_in, f_cool, tuple(f_missing), q))) % 10**6}"
                ev = _dataframe(
                    df, hide_index=True, selection_mode="multi-row", on_select="rerun", key=f"acct_table_{sel_ver}",
                    height=min(38 + 35 * len(df), 420),
                    column_config={
                        "Customer": st.column_config.TextColumn("Customer", width=170),
                        "Type": st.column_config.TextColumn("Type", width=105),
                        "Industry": st.column_config.TextColumn("Industry", width=110),
                        "Ends": st.column_config.DateColumn("Contract ends", format="MMM YYYY", width=95),
                        "Left": st.column_config.NumberColumn("Months left", width=70),
                        "Ideas": st.column_config.TextColumn("Top ideas", width=220),
                        "Contact": st.column_config.TextColumn("Contact", width=110),
                        "Worked": st.column_config.TextColumn("Emailed", width=70),
                        "Zoho": st.column_config.LinkColumn("Zoho", display_text="Open ↗", width=58),
                    },
                )
                sel = [rows[i] for i in (ev.selection.rows if ev else []) if i < len(rows)]
                st.session_state["selected_any"] = bool(sel)
                fresh = [a for a in rows if a["id"] not in queue]
                if not sel:
                    render_html(f'<div class="pe-hint">{icon("pointer", 16)}{len(rows):,} customers match. '
                                "Tick the ones to email, or add the next batch in one go.</div>")
                    if st.button(f"➕  Add the next {min(len(fresh), MAX_BATCH)} to review", type="primary",
                                 disabled=not fresh, **FULL_WIDTH):
                        add_to_queue(fresh[:MAX_BATCH])
                        st.rerun()
                else:
                    if st.button(f"➕  Add {len(sel)} selected to review", type="primary", **FULL_WIDTH):
                        add_to_queue(sel[:100])
                        st.rerun()

# ---------------- Right: account dossier ----------------
queue_order: List[str] = [a for a in st.session_state["queue_order"] if a in queue]
with col_right:
    with st.container(key="card-right"):
        if not queue:
            render_html(
                f'<div class="pe-empty"><div style="color:var(--accent);display:inline-block;'
                f'padding:18px;border-radius:20px;background:var(--accent-soft);border:1px solid rgba(124,131,255,.3)">'
                f'{icon("target", 40, 1.6)}</div>'
                '<div class="t">Each customer\'s card will appear here</div>'
                '<div class="s">Their services, contract dates, the best ideas for them, and a tailored email'
                ' in their own brand.</div>'
                "<ol><li>Load your customers</li><li>Filter and add some to review</li>"
                "<li>Check the ideas, then <b>&nbsp;Send via Zoho</b></li></ol></div>")
        else:
            log_now = get_sent_log()
            if st.session_state.get("current_id") not in queue:
                st.session_state["current_id"] = queue_order[0]
            if len(queue_order) > 1:
                if st.session_state.get("current_id_select") not in queue:
                    st.session_state["current_id_select"] = st.session_state["current_id"]
                st.selectbox(f"Viewing customer ({len(queue_order)} in review)", queue_order, key="current_id_select",
                             format_func=lambda a: ("✓ " if a in log_now else "") + queue[a]["acct"].get("Account_Name", a))
                st.session_state["current_id"] = st.session_state["current_id_select"]
            aid = st.session_state["current_id"]
            item = queue[aid]
            acct, snap, brand = item["acct"], item["snap"], item["brand"]
            section_header("03", "Customer card", "Check the ideas, tweak the email and send.")
            ml = snap["months_left"]
            meta = [chip(acct.get("_type") or "Customer"), chip(brand["name"], "accent"),
                    chip(snap["profile"]["name"], "muted")]
            if ml is not None:
                meta.append(chip(("Contract ended" if ml < 0 else f"Ends {snap['end'].strftime('%b %Y')}"),
                                 "risk" if ml < 3 else "warn" if ml <= 12 else "good"))
            if snap["months_in"] is not None:
                yrs = snap["months_in"] / 12
                meta.append(chip(f"Customer {yrs:.1f} yrs" if yrs >= 1 else f"Customer {int(snap['months_in'])} mths", "muted"))
            if aid in log_now:
                meta.append(chip(f"Emailed {sent_label(log_now[aid])[2:]}", "good"))
            render_html(f'<div class="pe-firm"><div><div class="name">{esc(acct.get("Account_Name", ""))}</div>'
                        f'<div class="meta">{"".join(meta)}</div></div></div>')
            z1, z2 = columns([1.7, 1])
            with z2:
                st.link_button("Open in Zoho ↗", ZOHO.record_url("Accounts", aid), **FULL_WIDTH)
            if item["brand_fallback"]:
                st.info(f"{acct.get('_type')} brand details aren't filled in yet, so this email uses SY Communications."
                        " Add them under Brand details.")

            # Services at a glance
            svc = []
            for k in ("broadband", "mobiles", "call_scope", "integration", "cctv", "headsets", "networking"):
                state = snap["has"].get(k)
                svc.append(chip(("✓ " if state else "✗ " if state is False else "? ") + OFFER_TITLES[k],
                                "good" if state else "risk" if state is False else "muted"))
            extra = []
            if snap["users"]:
                extra.append(f"{snap['users']} users")
            extra.append(f"Contract {fmt_date(snap['start'])} → {fmt_date(snap['end'])}")
            render_html('<div class="pe-panel"><div class="h">What they have with us</div>'
                        f'<div class="pe-chips">{"".join(svc)}</div>'
                        f'<div style="font-size:.8rem;color:var(--muted);margin-top:8px">{esc(" · ".join(extra))}'
                        "<br>✓ has it · ✗ doesn't · ? not recorded in Zoho</div></div>")

            # Contact
            if item["contacts"]:
                labels = [f"{contact_name(c) or 'No name'} · {c.get('Title') or 'no title'} · {c.get('Email')}"
                          + ("  (opted out)" if c.get("Email_Opt_Out") else "") for c in item["contacts"]]
                new_idx = st.selectbox("Send to", list(range(len(labels))), index=item["contact_idx"],
                                       format_func=lambda i: labels[i], key=f"contact_{aid}")
                if new_idx != item["contact_idx"]:
                    item["contact_idx"] = new_idx
                    item["sig"] = None
                    bump()
                if current_contact(item).get("Email_Opt_Out"):
                    st.warning("This contact has opted out of email in Zoho. Pick someone else, or call instead.")
            else:
                st.warning("No contact with an email address on this account in Zoho. Add one in Zoho, then reload.")

            # Ideas
            why = {k: w for k, _, w in item["ranked"]}
            new_offers = st.multiselect(
                "Ideas to include", [k for k, _, _ in item["ranked"]], default=[o for o in item["offers"] if o in why],
                format_func=lambda k: f"{OFFER_TITLES[k]} · {why.get(k, '')}", key=f"offers_{aid}",
                help="Best ideas first. The first one sets the subject line.")
            if new_offers != item["offers"]:
                item["offers"] = new_offers
                item["sig"] = None
                bump()

            ensure_draft(item)
            wsig = (aid, item["sig"])
            if st.session_state.get("email_widget_sig") != wsig:
                st.session_state["email_subject"] = item["subject"]
                st.session_state["email_body"] = item["body"]
                st.session_state["email_widget_sig"] = wsig
            st.session_state["opt_branded"] = st.toggle("Branded email design", value=st.session_state["opt_branded"],
                                                        key="w_opt_branded",
                                                        help=f"On: {brand['name']} header, idea cards and a call button.")
            subj = st.text_input("Subject", key="email_subject")
            body = st.text_area("Email body", key="email_body", height=340)
            item["subject"], item["body"] = subj, body
            with st.expander("👀  Preview the email as they'll see it"):
                components.html(email_html(body, subj, brand), height=820, scrolling=True)
            to = item_email(item)
            if aid not in log_now and to and item["offers"]:
                try:
                    zpop = st.popover("🚀  Send this email via Zoho", key=f"zs1_{aid}_{st.session_state['sent_log_ver']}",
                                      **FULL_WIDTH)
                except TypeError:
                    zpop = st.popover("🚀  Send this email via Zoho", **FULL_WIDTH)
                with zpop:
                    senders, s_err = zoho_senders()
                    if s_err:
                        st.caption(s_err)
                    else:
                        frm = pick_from(senders, brand, st.session_state.get("zs_from", 0))
                        st.markdown(f"Send to **{esc(to)}** from **{esc(frm['email']) if frm else '?'}**?")
                        st.caption("Logged on the contact in Zoho, with a note on the account.")
                        if st.button("Yes, send it now", type="primary", key=f"zs1_go_{aid}", **FULL_WIDTH):
                            push_to_zoho([aid], st.session_state.get("zs_from", 0), origin="dossier")
                            st.rerun()
            show_push_result("dossier")
            is_sent = aid in log_now
            chk = st.checkbox("✅  Handled (emailed or dealt with another way)", value=is_sent,
                              key=f"handled_{aid}_{st.session_state['sent_log_ver']}")
            if chk != is_sent:
                record_sent({aid: sent_record(item) if chk else None})
                st.rerun()

# ---------------- Review & send (full width) ----------------
if queue:
    with st.container(key="card-queue"):
        log_now = get_sent_log()
        for a in queue_order:
            ensure_draft(queue[a])
        ready_ids = [a for a in queue_order if a not in log_now and item_email(queue[a]) and queue[a]["offers"]]
        noemail_ids = [a for a in queue_order if a not in log_now and not item_email(queue[a])]
        noidea_ids = [a for a in queue_order if a not in log_now and item_email(queue[a]) and not queue[a]["offers"]]
        handled_ids = [a for a in queue_order if a in log_now]
        ver = st.session_state.get("queue_ver", 0)
        section_header("04", "Review & send",
                       f"{len(queue_order)} in review · {len(ready_ids)} ready · {len(noemail_ids)} no contact email"
                       f" · {len(handled_ids)} handled")
        show_push_result("panel")
        render_html('<div style="font-weight:700;margin:14px 0 6px 0">✉️ Ready to email '
                    f'{chip(str(len(ready_ids)), "good")}</div>')
        if noidea_ids:
            st.caption(f"{len(noidea_ids)} customer(s) have no ideas picked, so they're held back. Open their card to add some.")
        if ready_ids:
            rdf = pd.DataFrame([{
                "id": a, "Select": bool(queue[a]["include"]), "Handled": False,
                "Customer": queue[a]["acct"].get("Account_Name", ""), "Brand": queue[a]["brand"]["name"],
                "Contact": contact_name(current_contact(queue[a])), "Email": item_email(queue[a]),
                "Ideas": ", ".join(OFFER_TITLES.get(o, o) for o in queue[a]["offers"]),
                "Subject": queue[a]["subject"],
            } for a in ready_ids])
            edited = _data_editor(
                rdf, hide_index=True, num_rows="fixed", key=f"q_ready_{ver}", height=min(38 + 35 * len(rdf), 390),
                column_order=["Select", "Handled", "Customer", "Brand", "Contact", "Email", "Ideas", "Subject"],
                disabled=["Customer", "Brand", "Contact", "Email", "Ideas", "Subject"],
                column_config={"Select": st.column_config.CheckboxColumn("Select", width="small"),
                               "Handled": st.column_config.CheckboxColumn("Handled ✓", width="small")})
            changes: Dict[str, Optional[Dict[str, Any]]] = {}
            for _, r in edited.iterrows():
                queue[r["id"]]["include"] = bool(r["Select"])
                if r["Handled"]:
                    changes[r["id"]] = sent_record(queue[r["id"]])
            if changes:
                record_sent(changes)
                st.rerun()
            sel_ids = [a for a in ready_ids if queue[a]["include"]]

            with st.container(key="card-zoho-send"):
                senders, s_err = zoho_senders()
                if s_err:
                    if "permission" in s_err.lower() or "scope" in s_err.lower():
                        st.info("Sending needs the full Zoho permissions. Generate a new code with the scope below,"
                                " connect, then replace ZOHO_REFRESH_TOKEN in Secrets and reboot.")
                        with st.expander("Upgrade Zoho permissions"):
                            render_zoho_setup()
                    else:
                        st.error(s_err)
                elif senders:
                    st.selectbox("Send from (when a brand's own address isn't set up in Zoho)", list(range(len(senders))),
                                 key="zs_from",
                                 format_func=lambda i: f"{senders[i].get('user_name') or ''} <{senders[i]['email']}>".strip())
                    unmatched = sorted({queue[a]["brand"]["name"] for a in sel_ids
                                        if not any(s_.get("email", "").lower() == (queue[a]["brand"].get("email") or "").lower()
                                                   for s_ in senders)})
                    if unmatched:
                        st.caption("ℹ️ Zoho has no From address for " + ", ".join(unmatched)
                                   + ", so those go from the address above. Add the brand's address in Zoho"
                                     " (Setup → Channels → Email → Organization Emails) to send as the brand.")
                    sent_today = zoho_sent_today(log_now)
                    left = max(0, ZOHO_SEND_LIMIT - sent_today)
                    ids = sel_ids[:left]
                    if len(sel_ids) > left:
                        st.warning(f"Zoho allows {ZOHO_SEND_LIMIT} emails a day and {sent_today} have gone today,"
                                   f" so only the first {left} will be sent.")
                    label = f"🚀  Send {len(ids)} {'email' if len(ids) == 1 else 'emails'} via Zoho"
                    try:
                        pop = st.popover(label, key=f"zs_pop_{st.session_state['sent_log_ver']}", disabled=not ids,
                                         **FULL_WIDTH)
                    except TypeError:
                        pop = st.popover(label, disabled=not ids, **FULL_WIDTH)
                    with pop:
                        st.markdown(f"Send **{len(ids)} emails** now, each in the customer's own brand?")
                        st.caption("This can't be undone. Each is logged on the contact in Zoho with a note on the account.")
                        if st.button("Yes, send them now", type="primary", key="zs_confirm", **FULL_WIDTH):
                            push_to_zoho(ids, st.session_state.get("zs_from", 0))
                            st.rerun()
                    st.caption(f"Sent via Zoho today: {sent_today} of {ZOHO_SEND_LIMIT}.")
        else:
            st.caption("Nobody ready to email yet.")

        render_html('<div style="font-weight:700;margin:18px 0 6px 0">📞 No contact email '
                    f'{chip(str(len(noemail_ids)), "warn")}</div>')
        if noemail_ids:
            st.caption("These accounts have no contact with an email in Zoho (or they opted out). Call them, or add a"
                       " contact in Zoho and reload.")
            ndf = pd.DataFrame([{
                "Customer": queue[a]["acct"].get("Account_Name", ""), "Phone": queue[a]["acct"].get("Phone") or "",
                "Ideas": ", ".join(OFFER_TITLES.get(o, o) for o in queue[a]["offers"]),
                "Contract ends": fmt_date(queue[a]["snap"]["end"]),
                "Zoho": ZOHO.record_url("Accounts", a),
            } for a in noemail_ids])
            _dataframe(ndf, hide_index=True, column_config={"Zoho": st.column_config.LinkColumn("Zoho", display_text="Open ↗")})
            st.download_button("📋  Call list (.csv)", ndf.to_csv(index=False).encode("utf-8-sig"),
                               file_name=f"Customer_Growth_call_list_{now_uk().strftime('%Y-%m-%d')}.csv",
                               mime="text/csv")
        if handled_ids:
            with st.expander(f"✓ Handled ({len(handled_ids)})"):
                _dataframe(pd.DataFrame([{
                    "Customer": queue[a]["acct"].get("Account_Name", ""),
                    "Status": f"{log_now[a].get('status', '')} {sent_label(log_now[a])[2:]}",
                    "Sent to": log_now[a].get("to", ""), "Ideas": ", ".join(log_now[a].get("offers") or []),
                    "By": log_now[a].get("sent_by", ""),
                } for a in handled_ids]), hide_index=True)
        st.write("")
        if st.button("Clear review", help="Empty the review list (sent ticks are kept)."):
            st.session_state["queue"], st.session_state["queue_order"] = {}, []
            bump()
            st.rerun()

# ---------------- Late-rendered pieces ----------------
active_step = 4 if queue else 3 if st.session_state.get("selected_any") else 2 if st.session_state.get("accts") else 1
render_html(hero_html(active_step), target=hero_slot)
render_html(
    '<div class="pe-stats">'
    f'<div class="pe-stat"><div class="v">{len(st.session_state.get("accts") or [])}</div><div class="l">Loaded</div></div>'
    f'<div class="pe-stat"><div class="v">{len(queue)}</div><div class="l">In review</div></div>'
    f'<div class="pe-stat"><div class="v">{zoho_sent_today(get_sent_log())}</div><div class="l">Sent today</div></div>'
    "</div>",
    target=sidebar_stats_slot,
)
