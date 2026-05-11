import re
import base64
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="COMAE — Painel Gerencial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Background ───────────────────────────────────────────────────────────────

@st.cache_resource
def _load_bg() -> str:
    p = Path(__file__).parent / "helicopter.jpg"
    if not p.exists():
        return ""
    with open(p, "rb") as f:
        return base64.b64encode(f.read()).decode()

_BG_B64 = _load_bg()
_BG_CSS = (
    f"background: linear-gradient(rgba(10,13,20,0.87),rgba(10,13,20,0.87)), "
    f"url('data:image/jpeg;base64,{_BG_B64}') center/cover fixed !important;"
) if _BG_B64 else "background-color: #0d1117 !important;"

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
[data-testid="stSidebar"],[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"],button[kind="header"]{{display:none!important}}
#MainMenu,footer,header{{visibility:hidden}}
.block-container{{padding:1.5rem 2rem 2rem!important;max-width:100%!important}}
.stApp{{{_BG_CSS}}}
[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stHeader"]{{
    background:transparent!important}}

/* ── KPI cards ── */
[data-testid="metric-container"]{{
    background:rgba(18,22,32,0.76)!important;
    backdrop-filter:blur(18px) saturate(160%)!important;
    -webkit-backdrop-filter:blur(18px) saturate(160%)!important;
    border:1px solid rgba(251,191,36,0.18)!important;
    border-top:2px solid rgba(245,158,11,0.55)!important;
    border-radius:14px;padding:16px 20px;
    box-shadow:0 4px 28px rgba(0,0,0,0.5);
}}
[data-testid="stMetricLabel"]{{
    color:rgba(148,163,184,0.65)!important;font-size:11px!important;
    font-weight:700!important;letter-spacing:0.08em!important;text-transform:uppercase!important}}
[data-testid="stMetricValue"]{{color:#fbbf24!important;font-weight:800!important}}
[data-testid="stMetricDelta"]{{color:#4ade80!important}}

/* ── Inputs ── */
[data-baseweb="select"]>div{{
    background:rgba(22,27,39,0.75)!important;backdrop-filter:blur(12px)!important;
    border-color:rgba(30,42,58,0.8)!important;border-radius:10px!important;color:#e2e8f0!important}}
[data-testid="stTextInput"]>div{{
    background:rgba(22,27,39,0.75)!important;backdrop-filter:blur(12px)!important;
    border-radius:10px!important;border-color:rgba(30,42,58,0.8)!important}}
input[type="text"]{{background:transparent!important;color:#e2e8f0!important}}

/* ── Dropdown options ── */
[data-baseweb="popover"]{{z-index:9999!important}}
[data-baseweb="menu"] li,[data-baseweb="menu"] li>div,[data-baseweb="menu"] li>div>div{{
    white-space:normal!important;height:auto!important;min-height:36px!important;
    line-height:1.45!important;overflow:visible!important;text-overflow:unset!important}}
[data-baseweb="menu"] li>div>div>span{{
    white-space:normal!important;overflow:visible!important;
    text-overflow:unset!important;display:block!important;word-break:break-word!important}}
[data-baseweb="tag"] span{{white-space:normal!important;overflow:visible!important;max-width:none!important}}

/* ── Botões secundários ── */
[data-testid="baseButton-secondary"],.stButton>button{{
    background:rgba(22,27,39,0.75)!important;backdrop-filter:blur(12px)!important;
    border:1px solid rgba(45,63,82,0.8)!important;color:#94a3b8!important;
    border-radius:10px!important;overflow:hidden!important;
    display:flex!important;align-items:center!important;
    justify-content:center!important;line-height:1!important;padding:6px 4px!important}}

/* ── Botão primário ── */
[data-testid="baseButton-primary"],button[kind="primary"],
button[kind="primaryFormSubmit"],.stFormSubmitButton>button,
.stButton>button[kind="primary"],.stButton>button[kind="primaryFormSubmit"]{{
    background:linear-gradient(135deg,#f59e0b,#d97706)!important;
    color:#0a0d14!important;border:none!important;border-radius:10px!important;
    font-weight:800!important;letter-spacing:0.06em!important;
    box-shadow:0 2px 16px rgba(245,158,11,0.35)!important;
    overflow:hidden!important;display:flex!important;align-items:center!important;
    justify-content:center!important}}
[data-testid="baseButton-primary"]:hover,.stFormSubmitButton>button:hover{{
    background:linear-gradient(135deg,#fbbf24,#f59e0b)!important;
    box-shadow:0 4px 24px rgba(251,191,36,0.5)!important}}

hr{{border-color:rgba(251,191,36,0.12)!important}}

/* ── Section title ── */
.section-title{{
    font-size:11px;font-weight:700;color:#94a3b8;
    border-left:3px solid #f59e0b;padding-left:10px;
    margin:8px 0 4px 0;letter-spacing:.12em;text-transform:uppercase}}

/* ── Tabs ── */
[data-baseweb="tab-list"]{{
    background:rgba(18,22,32,0.7)!important;
    border-bottom:1px solid rgba(251,191,36,0.18)!important;
    gap:0!important;padding:0 8px!important}}
[data-baseweb="tab"]{{
    color:#64748b!important;font-weight:600!important;
    font-size:13px!important;padding:10px 20px!important;
    border-radius:0!important;border-bottom:2px solid transparent!important}}
[aria-selected="true"][data-baseweb="tab"]{{
    color:#fbbf24!important;
    border-bottom:2px solid #f59e0b!important;
    background:rgba(251,191,36,0.07)!important}}
[data-baseweb="tab-panel"]{{background:transparent!important;padding:0!important}}

/* ── NC / NE Table ── */
.nc-wrap details>summary{{list-style:none}}
.nc-wrap details>summary::-webkit-details-marker{{display:none}}
.nc-hdr{{display:flex;align-items:center;padding:7px 16px;
         border-bottom:1px solid rgba(251,191,36,0.15)}}
.nc-hc{{padding-right:16px;color:rgba(148,163,184,0.55);font-size:10px;
        font-weight:700;text-transform:uppercase;letter-spacing:.10em}}
.nc-wrap details>summary{{
    display:flex;align-items:center;padding:10px 16px;cursor:pointer;
    border-bottom:1px solid rgba(30,42,58,0.5);transition:background .15s}}
.nc-wrap details>summary::before{{
    content:"▶";color:#475569;font-size:10px;
    min-width:20px;flex-shrink:0;display:inline-block}}
.nc-wrap details[open]>summary::before{{content:"▼";color:#f59e0b}}
.nc-wrap details>summary:hover{{background:rgba(245,158,11,.05)}}
.nc-wrap details[open]>summary{{background:rgba(245,158,11,.07)}}
.nc-num-block{{
    min-width:175px;padding-right:16px;flex-shrink:0;
    display:flex;flex-direction:column;gap:2px}}
.nc-nc{{color:#fbbf24;font-family:monospace;font-weight:600;font-size:12px}}
.nc-dt{{color:#475569;font-size:10px}}
.nc-op{{min-width:110px;padding-right:16px;font-size:11px;font-weight:600;flex-shrink:0}}
.nc-ped{{color:#2dd4bf;font-family:monospace;flex:1;padding-right:16px;
         font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.nc-tot{{font-family:monospace;font-weight:700;min-width:155px;font-size:12px;
         text-align:right;flex-shrink:0}}
.nc-det{{background:rgba(10,13,20,0.5);padding:12px 24px 14px 36px;
         border-bottom:1px solid rgba(30,42,58,0.5)}}
.nc-det-desc{{color:#475569;font-size:11px;margin:0 0 10px;line-height:1.5}}
.nc-det-desc strong{{color:#94a3b8;font-weight:600}}
.det-th{{padding:4px 10px;text-align:left;color:#475569;font-size:10px;
         font-weight:700;text-transform:uppercase;letter-spacing:.06em}}
.det-td{{padding:6px 10px;border-bottom:1px solid rgba(30,42,58,0.4)}}
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def fmt_brl(v):
    if pd.isna(v) or v != v:
        return "R$ 0,00"
    s = f"{abs(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}" if v >= 0 else f"-R$ {s}"


def parse_br(raw):
    s = str(raw).strip().replace("\xa0", "").replace(" ", "")
    if not s or s in ("nan", "NaN", "-", ""):
        return float("nan")
    if re.search(r",\d{1,2}$", s):
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return float("nan")


def chart_cfg():
    return {"displayModeBar": False}


def chart_layout(height=300, angle=0):
    return dict(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", size=11), height=height,
        margin=dict(l=0, r=120, t=10, b=0),
        xaxis=dict(gridcolor="rgba(30,42,58,0.6)", tickangle=angle,
                   showline=False, zeroline=False),
        yaxis=dict(gridcolor="rgba(30,42,58,0.6)", showline=False, zeroline=False),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
    )


def _vc(v):
    return "#4ade80" if v >= 0 else "#f87171"


def _oc(op):
    return "#a78bfa" if op == "ZIDA" else "#f59e0b"


# ─── NC TABLE HTML ─────────────────────────────────────────────────────────────

def build_nc_html(ncs: pd.DataFrame, d: pd.DataFrame) -> str:
    rows = []
    for _, row in ncs.iterrows():
        nc   = row["NC"]
        dt   = row["Data"].strftime("%d/%m/%Y") if pd.notna(row["Data"]) else "—"
        op   = row["Operacao"]
        ped  = row["Nr_Pedido"]
        tot  = row["Total"]
        desc = str(row["Descricao"])

        linhas = d[d["NC"] == nc]
        det_rows = ""
        for _, lr in linhas.iterrows():
            ldt = lr["Data_Emissao"].strftime("%d/%m/%Y") if pd.notna(lr["Data_Emissao"]) else "—"
            lv  = lr["Valor"]
            det_rows += (
                f"<tr><td class='det-td' style='color:#94a3b8;white-space:nowrap'>{ldt}</td>"
                f"<td class='det-td' style='color:#e2e8f0;font-size:11px'>{str(lr['UG_Cred'])[:50]}</td>"
                f"<td class='det-td' style='color:#64748b;font-size:11px'>{str(lr['Natureza_Despesa'])[:35]}</td>"
                f"<td class='det-td' style='text-align:right;font-family:monospace;"
                f"color:{_vc(lv)};white-space:nowrap'>{fmt_brl(lv)}</td></tr>"
            )

        rows.append(
            f"<details><summary>"
            f"<span class='nc-num-block'><span class='nc-nc'>NC {nc}</span>"
            f"<span class='nc-dt'>{dt}</span></span>"
            f"<span class='nc-op' style='color:{_oc(op)}'>{op}</span>"
            f"<span class='nc-ped'>{ped}</span>"
            f"<span class='nc-tot' style='color:{_vc(tot)}'>{fmt_brl(tot)}</span>"
            f"</summary>"
            f"<div class='nc-det'><p class='nc-det-desc'><strong>Descrição:</strong> {desc[:250]}</p>"
            f"<table style='width:100%;border-collapse:collapse'>"
            f"<thead><tr style='border-bottom:1px solid rgba(51,65,85,0.5)'>"
            f"<th class='det-th'>Data</th><th class='det-th'>UG Cred</th>"
            f"<th class='det-th'>Natureza</th><th class='det-th' style='text-align:right'>Valor</th>"
            f"</tr></thead><tbody>{det_rows}</tbody></table></div></details>"
        )

    n = len(ncs)
    rows_html = "\n".join(rows)
    return f"""
<div style='background:rgba(22,27,39,0.76);backdrop-filter:blur(18px) saturate(160%);
            -webkit-backdrop-filter:blur(18px) saturate(160%);
            border:1px solid rgba(251,191,36,0.14);border-radius:0 0 16px 16px;
            overflow:hidden;box-shadow:0 4px 32px rgba(0,0,0,0.5)'>
  <div style='padding:20px 24px 0'><div style='font-size:10px;font-weight:700;
      color:rgba(148,163,184,0.55);letter-spacing:.12em;text-transform:uppercase;
      margin-bottom:14px;border-left:3px solid #f59e0b;padding-left:10px'>
      Notas de Crédito &nbsp;·&nbsp; {n} registros</div></div>
  <div class='nc-wrap' style='overflow-x:auto'>
    <div class='nc-hdr'>
      <span style='min-width:20px'></span>
      <span class='nc-hc' style='min-width:175px'>NC / Data</span>
      <span class='nc-hc' style='min-width:110px'>Operação</span>
      <span class='nc-hc' style='flex:1'>Nr. Pedido</span>
      <span class='nc-hc' style='min-width:155px;text-align:right'>Total</span>
    </div>
    {rows_html}
  </div>
</div>"""


# ─── NE TABLE HTML ─────────────────────────────────────────────────────────────

def build_ne_html(ne_df: pd.DataFrame) -> str:
    rows = []
    for _, row in ne_df.iterrows():
        ne  = str(row["NE"])
        uni = str(row["Unidade"])[:45]
        emp = row["Empenhado"]
        apg = row["A_Pagar"]
        pgo = row["Pago"]
        tot = row["Total"]
        fav  = str(row["Favorecido"])[:80]
        desc = str(row["Descricao"])[:250]
        pag  = str(row["PAG"])

        rows.append(
            f"<details><summary>"
            f"<span class='nc-num-block'><span class='nc-nc'>NE {ne}</span>"
            f"<span class='nc-dt'>{uni}</span></span>"
            f"<span style='min-width:150px;padding-right:16px;font-family:monospace;"
            f"font-size:11px;color:#fbbf24;flex-shrink:0'>{fmt_brl(emp) if emp else '–'}</span>"
            f"<span style='min-width:150px;padding-right:16px;font-family:monospace;"
            f"font-size:11px;color:#f87171;flex-shrink:0'>{fmt_brl(apg) if apg else '–'}</span>"
            f"<span class='nc-tot' style='color:#4ade80'>{fmt_brl(pgo) if pgo else '–'}</span>"
            f"</summary>"
            f"<div class='nc-det'>"
            f"<div style='display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));"
            f"gap:8px 20px;font-size:11px'>"
            f"<div><span style='color:#64748b;font-weight:600'>Favorecido: </span>"
            f"<span style='color:#e2e8f0'>{fav}</span></div>"
            f"<div><span style='color:#64748b;font-weight:600'>PAG: </span>"
            f"<span style='color:#2dd4bf;font-family:monospace'>{pag}</span></div>"
            f"<div style='grid-column:1/-1'><span style='color:#64748b;font-weight:600'>Descrição: </span>"
            f"<span style='color:#e2e8f0'>{desc}</span></div>"
            f"</div></div></details>"
        )

    n = len(ne_df)
    rows_html = "\n".join(rows)
    return f"""
<div style='background:rgba(22,27,39,0.76);backdrop-filter:blur(18px) saturate(160%);
            -webkit-backdrop-filter:blur(18px) saturate(160%);
            border:1px solid rgba(251,191,36,0.14);border-radius:0 0 16px 16px;
            overflow:hidden;box-shadow:0 4px 32px rgba(0,0,0,0.5)'>
  <div style='padding:20px 24px 0'><div style='font-size:10px;font-weight:700;
      color:rgba(148,163,184,0.55);letter-spacing:.12em;text-transform:uppercase;
      margin-bottom:14px;border-left:3px solid #f59e0b;padding-left:10px'>
      Notas de Empenho &nbsp;·&nbsp; {n} registros</div></div>
  <div class='nc-wrap' style='overflow-x:auto'>
    <div class='nc-hdr'>
      <span style='min-width:20px'></span>
      <span class='nc-hc' style='min-width:175px'>NE / Unidade</span>
      <span class='nc-hc' style='min-width:150px;padding-right:16px'>Empenhado</span>
      <span class='nc-hc' style='min-width:150px;padding-right:16px'>A Pagar</span>
      <span class='nc-hc' style='min-width:155px;text-align:right'>Pago</span>
    </div>
    {rows_html}
  </div>
</div>"""


# ─── AUTH ─────────────────────────────────────────────────────────────────────

def show_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1.5, 1, 1.5])
    with col:
        st.markdown(
            "<div style='background:rgba(18,22,32,0.82);backdrop-filter:blur(20px);"
            "-webkit-backdrop-filter:blur(20px);"
            "border:1px solid rgba(251,191,36,0.2);border-top:2px solid rgba(245,158,11,0.6);"
            "border-radius:16px;padding:32px 28px;text-align:center'>"
            "<div style='font-size:28px;margin-bottom:8px'>✈️</div>"
            "<div style='font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;"
            "color:#f59e0b;margin-bottom:6px'>Painel Gerencial</div>"
            "<div style='font-size:16px;font-weight:900;letter-spacing:.06em;text-transform:uppercase;"
            "background:linear-gradient(90deg,#fbbf24,#f59e0b,#e2e8f0);-webkit-background-clip:text;"
            "-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:0'>"
            "Comando de Operações<br>Aeroespaciais</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar", use_container_width=True, type="primary")
        if submitted:
            try:
                u = st.secrets["users"][username]
                if u["password"] == password:
                    st.session_state.update(
                        logged_in=True, username=username,
                        display_name=u.get("name", username),
                    )
                    st.rerun()
                else:
                    st.error("Senha incorreta.")
            except KeyError:
                st.error("Usuário não encontrado.")


# ─── DATA — Crédito ───────────────────────────────────────────────────────────

SHEET_ID     = "1Hj0nsW57SrM2zcnacb6XwD2jk8rSaLOHHBfygUXvNX0"
GID          = "1793849595"
UGCRED_COMAE = "COMANDO DE OPERACOES AEROESPACIAIS"


@st.cache_data(ttl=1800, show_spinner="Carregando créditos…")
def load_data() -> pd.DataFrame:
    url = (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
           f"/export?format=csv&gid={GID}")
    try:
        df = pd.read_csv(url, skiprows=5, header=None, dtype=str)
    except Exception as e:
        st.error(f"Erro ao carregar planilha de créditos: {e}")
        return pd.DataFrame()

    if len(df.columns) < 8:
        st.error(f"Planilha de créditos retornou {len(df.columns)} colunas. Esperado 8.")
        return pd.DataFrame()

    df = df.iloc[:, :8].copy()
    df.columns = ["Data_Emissao", "NC", "Descricao", "UG_Codigo",
                  "UG_Cred", "Conta_Contabil", "Natureza_Despesa", "Valor"]
    df.replace({"nan": pd.NA, "": pd.NA}, inplace=True)
    for col in ("Data_Emissao", "NC", "Descricao"):
        df[col] = df[col].ffill()

    df["NC"] = df["NC"].astype(str).str.strip().str[-12:]
    df["Data_Emissao"] = pd.to_datetime(df["Data_Emissao"], dayfirst=True, errors="coerce")
    df["Valor"] = df["Valor"].apply(parse_br)
    df.dropna(subset=["Valor"], inplace=True)
    df = df[df["Valor"] != 0].copy()

    df["Operacao"] = df["Descricao"].apply(
        lambda x: "ZIDA" if "ZIDA" in str(x).upper() else "CATRIMANI")

    _RE_PED = re.compile(r"PEDIDO\s+NR[\.:]?\s*(\d[\d/]+)", re.IGNORECASE)
    df["Nr_Pedido"] = df["Descricao"].apply(
        lambda x: (m := _RE_PED.search(str(x))) and m.group(1) or "—")

    for c in ("UG_Cred", "Natureza_Despesa", "Descricao"):
        df[c] = df[c].astype(str).str.strip().replace("nan", "—")

    return df


# ─── DATA — Empenhos ──────────────────────────────────────────────────────────

EMP_SHEET_ID = "1kVZ56hipKe40-xEq9bLsmfuiIj1-C-pVhc8UCVl33jk"
EMP_GID      = "977328743"


@st.cache_data(ttl=1800, show_spinner="Carregando empenhos…")
def load_empenhos() -> pd.DataFrame:
    url = (f"https://docs.google.com/spreadsheets/d/{EMP_SHEET_ID}"
           f"/export?format=csv&gid={EMP_GID}")
    try:
        raw = pd.read_csv(url, header=None, dtype=str)
    except Exception as e:
        st.warning(f"Planilha de empenhos indisponível: {e}")
        return pd.DataFrame()

    if len(raw.columns) < 10:
        return pd.DataFrame()

    raw = raw.iloc[:, :10].copy()
    raw.columns = list("ABCDEFGHIJ")

    # Fill down coluna B (Unidade)
    raw["B"] = raw["B"].replace({"": pd.NA, "nan": pd.NA}).ffill()

    # Parse valores numéricos (H, I, J)
    for col in ["H", "I", "J"]:
        raw[col] = raw[col].apply(parse_br)

    # Filtra linhas com pelo menos um valor numérico e NE preenchida
    raw["Total"] = raw[["H", "I", "J"]].fillna(0).sum(axis=1)
    raw = raw[
        raw["C"].notna() &
        raw["C"].astype(str).str.strip().ne("") &
        (raw["Total"] != 0)
    ].copy()

    df_ne = pd.DataFrame({
        "Unidade":    raw["B"].astype(str).str.strip(),
        "NE":         raw["C"].astype(str).str.strip().str[-12:],
        "Favorecido": raw["E"].astype(str).str.strip().replace("nan", "—"),
        "Descricao":  raw["F"].astype(str).str.strip().replace("nan", "—"),
        "PAG":        raw["G"].astype(str).str.strip().replace("nan", "—"),
        "Empenhado":  raw["H"].fillna(0),
        "A_Pagar":    raw["I"].fillna(0),
        "Pago":       raw["J"].fillna(0),
        "Total":      raw["Total"],
    })

    return df_ne.reset_index(drop=True)


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

def run_dashboard():
    df    = load_data()
    df_ne = load_empenhos()
    if df.empty:
        st.stop()

    # ── Cabeçalho ─────────────────────────────────────────────────────────────
    user_name = st.session_state.get("display_name", "")
    st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:8px 0 16px 0;border-bottom:1px solid rgba(251,191,36,0.18);
            margin-bottom:4px">
  <div style="display:flex;align-items:center;gap:18px">
    <div style="width:52px;height:52px;
                background:linear-gradient(135deg,rgba(251,191,36,0.18),rgba(245,158,11,0.08));
                border:1px solid rgba(251,191,36,0.35);border-radius:12px;
                display:flex;align-items:center;justify-content:center;
                font-size:26px;box-shadow:0 0 20px rgba(251,191,36,0.15);
                flex-shrink:0;overflow:hidden">✈️</div>
    <div>
      <div style="font-size:11px;font-weight:700;letter-spacing:0.22em;
                  text-transform:uppercase;color:#f59e0b;margin-bottom:4px;
                  text-shadow:0 0 20px rgba(251,191,36,0.4)">Painel Gerencial</div>
      <div style="font-size:22px;font-weight:900;letter-spacing:0.06em;
                  text-transform:uppercase;line-height:1.1;
                  background:linear-gradient(90deg,#fbbf24 0%,#f59e0b 40%,#e2e8f0 100%);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  background-clip:text">Comando de Operações Aeroespaciais</div>
    </div>
  </div>
  <div style="font-size:12px;color:rgba(100,116,139,0.8);white-space:nowrap">
    👤 {user_name}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Filtros ────────────────────────────────────────────────────────────────
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    ug_opts_raw = sorted(set(df["UG_Cred"]) - {"—", "nan"})
    ug_opts     = ["Todas"] + ug_opts_raw
    comae_idx   = next(
        (i + 1 for i, u in enumerate(ug_opts_raw) if UGCRED_COMAE in u.upper()), 0)

    f1, f2, f3, f4, f5, f6 = st.columns([1.2, 3.8, 3.8, 2.5, 0.38, 0.38])
    with f1:
        op_sel = st.selectbox("Operação", ["Todos", "CATRIMANI", "ZIDA"],
                              label_visibility="collapsed")
    with f2:
        ug_sel = st.selectbox("UG Cred", ug_opts, index=comae_idx,
                              label_visibility="collapsed")
    with f3:
        nat_opts = sorted(set(df["Natureza_Despesa"]) - {"—", "nan"})
        nat_sel  = st.multiselect("Natureza", nat_opts, placeholder="Natureza Despesa",
                                  label_visibility="collapsed")
    with f4:
        search = st.text_input("Busca", placeholder="🔍 Busca livre…",
                               label_visibility="collapsed")
    with f5:
        if st.button("🔄", help="Atualizar dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with f6:
        if st.button("🚪", help="Sair", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    # ── Datasets ───────────────────────────────────────────────────────────────
    # d_base: op + nat + busca, sem filtro de UG (gráficos fixos)
    d_base = df.copy()
    if op_sel != "Todos":
        d_base = d_base[d_base["Operacao"] == op_sel]
    if nat_sel:
        d_base = d_base[d_base["Natureza_Despesa"].isin(nat_sel)]
    if search:
        m0 = d_base.apply(lambda r: search.lower() in r.astype(str).str.cat(sep=" ").lower(), axis=1)
        d_base = d_base[m0]

    # d: filtrado por tudo
    d = d_base.copy()
    if ug_sel != "Todas":
        d = d[d["UG_Cred"] == ug_sel]

    if d.empty:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
        return

    # Empenhos filtrados por UG (match substring)
    ne_filt = df_ne.copy()
    if not df_ne.empty and ug_sel != "Todas":
        term = ug_sel[:25].upper()
        ne_filt = df_ne[df_ne["Unidade"].str.upper().str.contains(term, na=False, regex=False)]
        if ne_filt.empty:
            ne_filt = df_ne.copy()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    st.divider()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_pos  = d[d["Valor"] > 0]["Valor"].sum()
    total_neg  = d[d["Valor"] < 0]["Valor"].sum()
    total_disp = total_pos + total_neg

    mask_comae     = d_base["UG_Cred"].str.upper().str.contains(UGCRED_COMAE, na=False)
    total_descentr = d_base[(d_base["Valor"] > 0) & (~mask_comae)]["Valor"].sum()
    total_empenhado = ne_filt["Total"].sum() if not ne_filt.empty else 0.0

    show_descentr = (ug_sel == "Todas") or (UGCRED_COMAE in ug_sel.upper())

    if show_descentr:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💰 Crédito Recebido",                   fmt_brl(total_pos))
        c2.metric("📊 Crédito Disponível",                 fmt_brl(total_disp))
        c3.metric("📋 Crédito Empenhado",                  fmt_brl(total_empenhado))
        c4.metric("📤 Crédito Descentralizado pelo COMAE", fmt_brl(total_descentr))
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Crédito Recebido",   fmt_brl(total_pos))
        c2.metric("📊 Crédito Disponível", fmt_brl(total_disp))
        c3.metric("📋 Crédito Empenhado",  fmt_brl(total_empenhado))

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Gráficos — linha 1: Recebido | Disponível ─────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">Crédito Recebido por UG</div>',
                    unsafe_allow_html=True)
        ug_rec = (
            d_base[d_base["Valor"] > 0]
            .groupby("UG_Cred", as_index=False)["Valor"].sum()
            .sort_values("Valor").tail(10)
        )
        ug_rec["fmt"] = ug_rec["Valor"].apply(fmt_brl)
        fig1 = px.bar(ug_rec, x="Valor", y="UG_Cred", orientation="h",
                      color_discrete_sequence=["#7c3aed"],
                      labels={"Valor": "", "UG_Cred": ""},
                      custom_data=["fmt"])
        fig1.update_traces(
            text=ug_rec["fmt"], textposition="outside",
            textfont=dict(size=9, color="#94a3b8"),
            hovertemplate="%{y}<br><b>%{customdata[0]}</b><extra></extra>",
            cliponaxis=False,
        )
        max_v1 = ug_rec["Valor"].max() if not ug_rec.empty else 1
        fig1.update_xaxes(range=[0, max_v1 * 1.45], tickformat=",.0f", showticklabels=False)
        fig1.update_layout(**chart_layout(max(280, len(ug_rec) * 42)))
        st.plotly_chart(fig1, use_container_width=True, config=chart_cfg())

    with col2:
        st.markdown('<div class="section-title">Crédito Disponível por Unidade</div>',
                    unsafe_allow_html=True)
        # Pré-computa natureza por UG para hover enriquecido
        nat_per_ug = (
            d_base.groupby(["UG_Cred", "Natureza_Despesa"])["Valor"]
            .sum().reset_index()
            .sort_values(["UG_Cred", "Valor"], ascending=[True, False])
        )
        def _nat_hover(ug_name):
            sub = nat_per_ug[nat_per_ug["UG_Cred"] == ug_name]
            return "<br>".join(
                f"• {r['Natureza_Despesa'][:35]}: {fmt_brl(r['Valor'])}"
                for _, r in sub.head(5).iterrows()
            ) or "—"

        ug_disp = (
            d_base.groupby("UG_Cred", as_index=False)["Valor"].sum()
            .rename(columns={"Valor": "Disponível"})
            .sort_values("Disponível").tail(10)
        )
        ug_disp["fmt"]      = ug_disp["Disponível"].apply(fmt_brl)
        ug_disp["nat_info"] = ug_disp["UG_Cred"].apply(_nat_hover)
        fig2 = px.bar(ug_disp, x="Disponível", y="UG_Cred", orientation="h",
                      color_discrete_sequence=["#f59e0b"],
                      labels={"Disponível": "", "UG_Cred": ""},
                      custom_data=["fmt", "nat_info"])
        fig2.update_traces(
            text=ug_disp["fmt"], textposition="outside",
            textfont=dict(size=9, color="#94a3b8"),
            hovertemplate=(
                "<b>%{y}</b><br>Disponível: %{customdata[0]}"
                "<br><br><i>Por Natureza:</i><br>%{customdata[1]}<extra></extra>"
            ),
            cliponaxis=False,
        )
        max_v2 = ug_disp["Disponível"].max() if not ug_disp.empty else 1
        fig2.update_xaxes(range=[0, max_v2 * 1.45], tickformat=",.0f", showticklabels=False)
        fig2.update_layout(**chart_layout(max(280, len(ug_disp) * 42)))
        st.plotly_chart(fig2, use_container_width=True, config=chart_cfg())

    # ── Gráficos — linha 2: Desc. por Mês | Desc. por Natureza ───────────────
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-title">Crédito Descentralizado por Mês</div>',
                    unsafe_allow_html=True)
        if show_descentr:
            td_neg = d[d["Valor"] < 0].copy()
            if not td_neg.empty:
                td_neg["Mes"]       = td_neg["Data_Emissao"].dt.to_period("M").astype(str)
                td_neg["Valor_abs"] = td_neg["Valor"].abs()
                ev_neg = td_neg.groupby(["Mes", "Operacao"], as_index=False)["Valor_abs"].sum()
                ev_neg["fmt"] = ev_neg["Valor_abs"].apply(fmt_brl)
                fig3 = px.bar(ev_neg, x="Mes", y="Valor_abs", color="Operacao", barmode="group",
                              color_discrete_map={"ZIDA": "#7c3aed", "CATRIMANI": "#f59e0b"},
                              labels={"Valor_abs": "", "Mes": "", "Operacao": "Operação"},
                              custom_data=["fmt"])
                fig3.update_traces(
                    text=ev_neg["fmt"], textposition="outside",
                    textfont=dict(size=8, color="#94a3b8"),
                    hovertemplate="%{x} · %{fullData.name}<br><b>%{customdata[0]}</b><extra></extra>",
                    cliponaxis=False,
                )
                max_v3 = ev_neg["Valor_abs"].max() if not ev_neg.empty else 1
                fig3.update_yaxes(range=[0, max_v3 * 1.4], tickformat=",.0f", showticklabels=False)
                fig3.update_layout(**chart_layout(300))
                st.plotly_chart(fig3, use_container_width=True, config=chart_cfg())
            else:
                st.info("Sem crédito descentralizado para os filtros selecionados.")
        else:
            st.markdown(
                "<div style='color:#475569;font-size:12px;padding:40px 0;text-align:center'>"
                "Este gráfico está disponível apenas para o COMAE.</div>",
                unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="section-title">Crédito Descentralizado por Natureza de Despesa</div>',
                    unsafe_allow_html=True)
        nat_neg = (
            d[d["Valor"] < 0]
            .groupby("Natureza_Despesa", as_index=False)["Valor"].sum()
        )
        if not nat_neg.empty:
            nat_neg["Valor"] = nat_neg["Valor"].abs()
            nat_neg = nat_neg.sort_values("Valor", ascending=False).head(8)
            nat_neg["fmt"] = nat_neg["Valor"].apply(fmt_brl)
            fig4 = px.bar(nat_neg, x="Natureza_Despesa", y="Valor",
                          color_discrete_sequence=["#f59e0b"],
                          labels={"Valor": "", "Natureza_Despesa": ""},
                          custom_data=["fmt"])
            fig4.update_traces(
                text=nat_neg["fmt"], textposition="outside",
                textfont=dict(size=8, color="#94a3b8"),
                hovertemplate="%{x}<br><b>%{customdata[0]}</b><extra></extra>",
                cliponaxis=False,
            )
            max_v4 = nat_neg["Valor"].max() if not nat_neg.empty else 1
            fig4.update_yaxes(range=[0, max_v4 * 1.4], tickformat=",.0f", showticklabels=False)
            fig4.update_layout(**chart_layout(300, angle=-30))
            st.plotly_chart(fig4, use_container_width=True, config=chart_cfg())
        else:
            st.info("Sem crédito descentralizado para os filtros selecionados.")

    # ── Gráfico — Empenhos por Unidade ────────────────────────────────────────
    if not ne_filt.empty:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Empenhos por Unidade</div>',
                    unsafe_allow_html=True)
        emp_ug = (
            ne_filt.groupby("Unidade", as_index=False)
            .agg(Empenhado=("Empenhado","sum"), A_Pagar=("A_Pagar","sum"), Pago=("Pago","sum"))
            .sort_values("Empenhado", ascending=True).tail(10)
        )
        emp_ug["fmt_emp"] = emp_ug["Empenhado"].apply(fmt_brl)
        emp_ug["fmt_apg"] = emp_ug["A_Pagar"].apply(fmt_brl)
        emp_ug["fmt_pgo"] = emp_ug["Pago"].apply(fmt_brl)

        fig5 = go.Figure()
        for col_key, label, color, fmt_col in [
            ("Empenhado", "Empenhado", "#fbbf24", "fmt_emp"),
            ("A_Pagar",   "A Pagar",   "#f87171", "fmt_apg"),
            ("Pago",      "Pago",      "#4ade80",  "fmt_pgo"),
        ]:
            fig5.add_trace(go.Bar(
                x=emp_ug[col_key], y=emp_ug["Unidade"], orientation="h",
                name=label, marker_color=color,
                text=emp_ug[fmt_col], textposition="outside",
                textfont=dict(size=8, color="#94a3b8"),
                customdata=emp_ug[[fmt_col]].values,
                hovertemplate=f"%{{y}}<br>{label}: <b>%{{customdata[0]}}</b><extra></extra>",
                cliponaxis=False,
            ))
        max_v5 = emp_ug[["Empenhado","A_Pagar","Pago"]].max().max() if not emp_ug.empty else 1
        fig5.update_xaxes(range=[0, max_v5 * 1.5], tickformat=",.0f", showticklabels=False)
        layout5 = chart_layout(max(300, len(emp_ug) * 55))
        layout5["barmode"] = "group"
        layout5["margin"]  = dict(l=0, r=180, t=30, b=0)
        layout5["legend"]  = dict(orientation="h", yanchor="bottom", y=1.02,
                                  xanchor="right", x=1, bgcolor="rgba(0,0,0,0)")
        fig5.update_layout(**layout5)
        st.plotly_chart(fig5, use_container_width=True, config=chart_cfg())

    # ── Tabelas — Tabs NC / NE ─────────────────────────────────────────────────
    st.divider()
    tab_nc, tab_ne = st.tabs(["📄  Notas de Crédito", "📋  Notas de Empenho"])

    with tab_nc:
        ncs = (
            d[d["Valor"] > 0]
            .groupby("NC", as_index=False)
            .agg(
                Data      = ("Data_Emissao", "first"),
                Descricao = ("Descricao",    "first"),
                Nr_Pedido = ("Nr_Pedido",    "first"),
                Operacao  = ("Operacao",     "first"),
                Total     = ("Valor",        "sum"),
            )
            .sort_values("Data", ascending=False)
        )
        st.markdown(build_nc_html(ncs, d), unsafe_allow_html=True)

    with tab_ne:
        if not ne_filt.empty:
            ne_show = ne_filt.sort_values("Total", ascending=False)
            st.markdown(build_ne_html(ne_show), unsafe_allow_html=True)
        else:
            st.info("Nenhum empenho encontrado para os filtros selecionados.")


# ─── ENTRADA ──────────────────────────────────────────────────────────────────

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    run_dashboard()
else:
    show_login()
