"""UI theme: CSS, dark mode overrides, and HTML component helpers."""

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg-main:        #F8FAFC;
    --bg-nav:         rgba(255, 255, 255, 0.94);
    --bg-card:        #FFFFFF;
    --bg-elevated:    #F1F5F9;
    --text-primary:   #0F172A;
    --text-secondary: #475569;
    --text-muted:     #64748B;
    --accent:         #4F46E5;
    --accent-hover:   #4338CA;
    --accent-2:       #06B6D4;
    --accent-rgb:     79, 70, 229;
    --border:         #E2E8F0;
    --border-subtle:  #F1F5F9;
    --shadow-sm:      0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);
    --shadow:         0 4px 16px -2px rgba(15, 23, 42, 0.07), 0 2px 6px -1px rgba(15, 23, 42, 0.04);
    --shadow-hover:   0 10px 24px -3px rgba(79, 70, 229, 0.12), 0 4px 8px -2px rgba(15, 23, 42, 0.04);
    --success:        #16A34A;
    --success-bg:     #F0FDF4;
    --warning:        #D97706;
    --warning-bg:     #FFFBEB;
    --error:          #DC2626;
    --error-bg:       #FEF2F2;
    --radius:         14px;
    --radius-sm:      8px;
    --radius-xs:      6px;
    --nav-h:          64px;
}

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg-main) !important;
    color: var(--text-primary) !important;
    -webkit-font-smoothing: antialiased;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header,
[data-testid="stHeader"],
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
.stDeployButton { display: none !important; }

/* Let main container be full width so sticky navbar touches edges */
[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
}
[data-testid="stMain"] { padding: 0 !important; }
[data-testid="stBottomBlockContainer"] { padding: 0 !important; }

/* ══════════════════════════════════════════════════════════
   NAVBAR: Single sticky header with Brand, Pills, Toggle
   ══════════════════════════════════════════════════════════ */
.st-key-sa-navbar {
    position: sticky !important;
    top: 0 !important;
    z-index: 9999 !important;
    background: var(--bg-nav) !important;
    border-bottom: 1px solid var(--border) !important;
    box-shadow: 0 1px 12px rgba(15, 23, 42, 0.04) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    padding: 0.55rem 2.5rem !important;
    width: 100% !important;
    margin: 0 !important;
}

.st-key-sa-navbar [data-testid="stHorizontalBlock"] {
    max-width: 1440px !important;
    margin: 0 auto !important;
    gap: 2rem !important;
    align-items: center !important;
    flex-wrap: nowrap !important;
    width: 100% !important;
}

.st-key-sa-navbar [data-testid="stColumn"] {
    min-width: 0 !important;
    display: flex !important;
    align-items: center !important;
}
.st-key-sa-navbar [data-testid="stColumn"]:first-child {
    min-width: max-content !important;
    padding-right: 1.5rem !important;
}
.st-key-sa-navbar [data-testid="stColumn"]:nth-child(2) {
    padding-left: 0.5rem !important;
}

/* Brand element */
.sa-brand {
    display: inline-flex;
    align-items: center;
    gap: 0.65rem;
    cursor: default;
    user-select: none;
    white-space: nowrap;
    text-decoration: none;
    padding-right: 1.5rem;
}
.sa-brand-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, rgba(var(--accent-rgb), 0.12), rgba(6, 182, 212, 0.12));
    border: 1px solid rgba(var(--accent-rgb), 0.22);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--accent);
    box-shadow: 0 2px 6px rgba(var(--accent-rgb), 0.12);
    flex-shrink: 0;
}
.sa-brand-icon svg {
    width: 20px;
    height: 20px;
}
.sa-brand-text {
    display: flex;
    align-items: center;
    gap: 0.65rem;
}
.sa-brand-title {
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: -0.025em;
    color: var(--text-primary);
    line-height: 1.2;
}
.sa-brand-badge {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    background: rgba(var(--accent-rgb), 0.09);
    color: var(--accent);
    padding: 0.18rem 0.5rem;
    border-radius: 4px;
    border: 1px solid rgba(var(--accent-rgb), 0.2);
    text-transform: uppercase;
    margin-right: 0.5rem;
}

/* Nav Pills Styling */
.st-key-sa-navbar [data-testid="stPills"] {
    display: flex !important;
    justify-content: center !important;
    gap: 0.4rem !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}
.st-key-sa-navbar [data-testid="stPills"] > div {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 0.35rem !important;
    justify-content: center !important;
}
.st-key-sa-navbar [data-testid="stPills"] button,
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pills"],
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pillsActive"] {
    border-radius: 20px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 0.95rem !important;
    height: 36px !important;
    min-height: 36px !important;
    box-shadow: none !important;
    white-space: nowrap !important;
    cursor: pointer !important;
    transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

/* Light mode unselected pill */
.st-key-sa-navbar [data-testid="stPills"] button,
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pills"] {
    background: #F1F5F9 !important;
    border: 1px solid #E2E8F0 !important;
    color: #475569 !important;
}
.st-key-sa-navbar [data-testid="stPills"] button:hover,
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pills"]:hover {
    background: rgba(79, 70, 229, 0.08) !important;
    color: #4F46E5 !important;
    border-color: rgba(79, 70, 229, 0.25) !important;
    transform: translateY(-1px) !important;
}

/* Light mode active pill */
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pillsActive"],
.st-key-sa-navbar [data-testid="stPills"] button[aria-checked="true"],
.st-key-sa-navbar [data-testid="stPills"] button[aria-selected="true"] {
    background: #4F46E5 !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-color: #4F46E5 !important;
    box-shadow: 0 2px 10px rgba(79, 70, 229, 0.35) !important;
}
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pillsActive"] p,
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pillsActive"] span,
.st-key-sa-navbar [data-testid="stPills"] button[aria-checked="true"] p,
.st-key-sa-navbar [data-testid="stPills"] button[aria-checked="true"] span,
.st-key-sa-navbar [data-testid="stPills"] button[aria-selected="true"] p,
.st-key-sa-navbar [data-testid="stPills"] button[aria-selected="true"] span {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Button styling in light mode */
[data-testid="stBaseButton-secondary"],
.stButton > button:not([data-testid="stBaseButton-primary"]):not([data-testid="baseButton-primary"]) {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    color: #0F172A !important;
}
[data-testid="stBaseButton-secondary"]:hover,
.stButton > button:not([data-testid="stBaseButton-primary"]):not([data-testid="baseButton-primary"]):hover {
    border-color: #4F46E5 !important;
    color: #4F46E5 !important;
    background: rgba(79, 70, 229, 0.04) !important;
}

/* Theme Toggle Button */
.st-key-theme_toggle {
    display: flex !important;
    justify-content: flex-end !important;
    width: 100% !important;
}
.st-key-theme_toggle button {
    width: 36px !important;
    height: 36px !important;
    min-height: 36px !important;
    border-radius: 50% !important;
    padding: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 1.05rem !important;
    border: 1px solid var(--border) !important;
    background: var(--bg-elevated) !important;
    color: var(--text-primary) !important;
    box-shadow: var(--shadow-sm) !important;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
}
.st-key-theme_toggle button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    transform: rotate(18deg) scale(1.08) !important;
    box-shadow: var(--shadow) !important;
}

/* ══════════════════════════════════════════════════════════
   PAGE CONTENT CONTAINER
   ══════════════════════════════════════════════════════════ */
.st-key-sa-page-body {
    max-width: 1440px !important;
    margin: 0 auto !important;
    padding: 2rem 2.5rem 5rem !important;
    width: 100% !important;
}

/* ── Page header ── */
.page-header {
    padding: 0 0 1.25rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.75rem;
}
.page-title {
    font-size: 1.75rem; font-weight: 700;
    letter-spacing: -0.03em; color: var(--text-primary);
    line-height: 1.2; margin-bottom: 0.35rem;
}
.page-subtitle { font-size: 0.9rem; color: var(--text-secondary); line-height: 1.55; }
.dataset-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    font-size: 0.75rem; font-weight: 500; color: var(--text-muted);
    background: var(--bg-elevated); border: 1px solid var(--border);
    border-radius: 20px; padding: 0.25rem 0.75rem;
    white-space: nowrap; margin-top: 0.65rem;
}
.dataset-badge-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--success); flex-shrink: 0;
    box-shadow: 0 0 6px rgba(22, 163, 74, 0.4);
}

/* ══════════════════════════════════════════════════════════
   CARDS SYSTEM (st.container border=True)
   ══════════════════════════════════════════════════════════ */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow-sm) !important;
    padding: 1.35rem 1.6rem !important;
    transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.18s ease !important;
    margin-bottom: 1.25rem !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: var(--shadow) !important;
    border-color: rgba(var(--accent-rgb), 0.25) !important;
}

/* Card Title Header */
.card-header-bar {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--text-muted);
    margin-bottom: 1.1rem;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid var(--border);
}
.card-header-bar svg, .card-header-bar .card-header-icon {
    font-size: 0.95rem;
    color: var(--accent);
}

/* Legacy content-card support */
.content-card-title {
    font-size: 0.8rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.07em; color: var(--text-muted);
    margin-bottom: 1rem; padding-bottom: 0.65rem;
    border-bottom: 1px solid var(--border);
    display: flex; align-items: center; gap: 0.4rem;
}

/* ── KPI Strip ── */
.kpi-strip {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem; margin-bottom: 1.75rem;
}
.kpi-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.15rem 1.25rem;
    box-shadow: var(--shadow-sm);
    display: flex; flex-direction: column; gap: 0.25rem;
    transition: box-shadow 0.2s ease, transform 0.18s ease, border-color 0.2s ease;
    min-width: 0;
}
.kpi-card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
    border-color: rgba(var(--accent-rgb), 0.3);
}
.kpi-icon-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.35rem; }
.kpi-icon {
    width: 34px; height: 34px; border-radius: var(--radius-sm);
    background: rgba(var(--accent-rgb), 0.08);
    border: 1px solid rgba(var(--accent-rgb), 0.15);
    display: flex; align-items: center; justify-content: center;
    font-size: 0.95rem; flex-shrink: 0;
}
.kpi-val { font-size: 1.55rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.03em; line-height: 1.1; word-break: break-all; }
.kpi-lbl { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-top: 0.15rem; }

/* ── Hero Section ── */
.hero-section {
    display: grid;
    grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
    gap: 3.5rem; align-items: center; padding: 1.5rem 0 2.75rem;
}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 0.45rem;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.09em;
    text-transform: uppercase; color: var(--accent);
    background: rgba(var(--accent-rgb), 0.08);
    border: 1px solid rgba(var(--accent-rgb), 0.2);
    border-radius: 20px; padding: 0.3rem 0.75rem; margin-bottom: 1.1rem;
}
.hero-title {
    font-size: clamp(2rem, 3.2vw, 2.85rem); font-weight: 800;
    line-height: 1.15; letter-spacing: -0.035em; color: var(--text-primary);
    margin-bottom: 1.1rem; word-break: break-word;
}
.grad-text {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
    -webkit-background-clip: text; background-clip: text;
    color: transparent; -webkit-text-fill-color: transparent;
}
.hero-desc {
    font-size: 0.98rem; line-height: 1.75; color: var(--text-secondary);
    margin-bottom: 1.75rem; max-width: 500px;
}
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.metric-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 1.15rem 1.25rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s ease, transform 0.18s ease, border-color 0.2s ease;
    min-width: 0;
}
.metric-card:hover {
    box-shadow: var(--shadow-hover);
    transform: translateY(-2px);
    border-color: rgba(var(--accent-rgb), 0.3);
}
.metric-icon-wrap {
    width: 36px; height: 36px; border-radius: var(--radius-sm);
    background: rgba(var(--accent-rgb), 0.08);
    border: 1px solid rgba(var(--accent-rgb), 0.15);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; margin-bottom: 0.65rem;
}
.metric-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.07em; color: var(--text-muted); margin-bottom: 0.25rem; }
.metric-value { font-size: 1.55rem; font-weight: 700; letter-spacing: -0.03em; color: var(--text-primary); line-height: 1.1; word-break: break-all; }
.metric-sub { font-size: 0.72rem; color: var(--text-muted); margin-top: 0.3rem; line-height: 1.4; }
.synthetic-badge {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.65rem; font-weight: 600; color: var(--warning);
    background: var(--warning-bg); border: 1px solid rgba(217, 119, 6, 0.25);
    border-radius: 20px; padding: 0.18rem 0.55rem; margin-top: 0.45rem;
}

/* ── Section Title ── */
.section-title { font-size: 1.4rem; font-weight: 700; letter-spacing: -0.025em; color: var(--text-primary); margin-bottom: 0.35rem; }
.section-sub { font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 1.5rem; line-height: 1.5; }

/* ── Research Cards ── */
.research-card-content {
    display: flex;
    flex-direction: column;
    height: 100%;
}
.research-card-icon {
    width: 42px; height: 42px; border-radius: var(--radius-sm);
    background: rgba(var(--accent-rgb), 0.08);
    border: 1px solid rgba(var(--accent-rgb), 0.15);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.15rem; margin-bottom: 0.85rem;
}
.research-card-title { font-size: 0.92rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.4rem; letter-spacing: -0.01em; }
.research-card-desc { font-size: 0.8rem; color: var(--text-secondary); line-height: 1.55; margin-bottom: 1rem; flex-grow: 1; }

/* ── Significance Badges ── */
.sig-yes { display: inline-flex; align-items: center; gap: 0.35rem; background: var(--success-bg); color: var(--success); border: 1px solid rgba(22,163,74,0.25); border-radius: 20px; padding: 0.2rem 0.75rem; font-size: 0.75rem; font-weight: 600; }
.sig-no  { display: inline-flex; align-items: center; gap: 0.35rem; background: var(--bg-elevated); color: var(--text-secondary); border: 1px solid var(--border); border-radius: 20px; padding: 0.2rem 0.75rem; font-size: 0.75rem; font-weight: 600; }

/* ── Footer ── */
.sa-footer {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem 2.5rem;
    text-align: center;
    margin-top: 3.5rem;
    box-shadow: var(--shadow-sm);
}
.sa-footer-title { font-size: 0.95rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.4rem; }
.sa-footer-text { font-size: 0.8rem; color: var(--text-muted); line-height: 1.7; }

/* ── Streamlit Widget Overrides ── */
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stSlider"] label,
[data-testid="stRadio"] label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.83rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
}
[data-testid="stDataFrame"] {
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    overflow: hidden;
}
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    background: var(--bg-card) !important;
    box-shadow: var(--shadow-sm) !important;
    margin-bottom: 1rem !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    padding: 0.75rem 1rem !important;
}
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--border);
    gap: 0.4rem;
    background: transparent;
    padding-bottom: 2px;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    color: var(--text-secondary) !important;
    border-radius: var(--radius-xs) var(--radius-xs) 0 0 !important;
    padding: 0.6rem 1.1rem !important;
    border: none !important;
    background: transparent !important;
    transition: color 0.15s ease !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    font-weight: 600 !important;
}
[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    border-left-width: 4px !important;
    font-size: 0.88rem !important;
}
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.9rem 1.1rem !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: var(--text-muted) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
    color: var(--text-primary) !important;
}
[data-testid="stBaseButton-primary"], [data-testid="baseButton-primary"] {
    background: var(--accent) !important;
    border: 1px solid var(--accent) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: 0 2px 8px rgba(var(--accent-rgb), 0.28) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stBaseButton-primary"]:hover, [data-testid="baseButton-primary"]:hover {
    background: var(--accent-hover) !important;
    box-shadow: 0 4px 14px rgba(var(--accent-rgb), 0.38) !important;
    transform: translateY(-1px) !important;
}
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.88rem !important;
    transition: all 0.2s ease !important;
}
[data-testid="stDownloadButton"] button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.88rem !important;
}

/* Responsive adjustments */
@media (max-width: 1200px) {
    .st-key-sa-page-body { padding: 1.75rem 2rem 4rem !important; }
    .st-key-sa-navbar { padding: 0.55rem 1.5rem !important; }
}
@media (max-width: 900px) {
    .hero-section { grid-template-columns: 1fr; gap: 2rem; }
    .kpi-strip { grid-template-columns: repeat(3, 1fr); }
    .st-key-sa-navbar [data-testid="stPills"] button { padding: 0.35rem 0.6rem !important; font-size: 0.78rem !important; }
}
@media (max-width: 640px) {
    .st-key-sa-page-body { padding: 1rem 1rem 3rem !important; }
    .st-key-sa-navbar { padding: 0.5rem 0.75rem !important; }
    .kpi-strip { grid-template-columns: repeat(2, 1fr); }
    .hero-title { font-size: 1.75rem; }
    .metric-grid { grid-template-columns: 1fr; }
}
</style>
"""

DARK_MODE_CSS = """
<style>
:root,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    --bg-main:        #090D16;
    --bg-nav:         rgba(13, 18, 30, 0.94);
    --bg-card:        #111726;
    --bg-elevated:    #172033;
    --text-primary:   #F8FAFC;
    --text-secondary: #94A3B8;
    --text-muted:     #64748B;
    --accent:         #6366F1;
    --accent-hover:   #818CF8;
    --accent-2:       #22D3EE;
    --accent-rgb:     99, 102, 241;
    --border:         #1E293B;
    --border-subtle:  #162032;
    --shadow-sm:      0 1px 3px rgba(0, 0, 0, 0.4);
    --shadow:         0 4px 20px rgba(0, 0, 0, 0.5);
    --shadow-hover:   0 12px 32px rgba(99, 102, 241, 0.22);
    --success:        #22C55E;
    --success-bg:     rgba(34, 197, 94, 0.12);
    --warning:        #F59E0B;
    --warning-bg:     rgba(245, 158, 11, 0.12);
    --error:          #F87171;
    --error-bg:       rgba(248, 113, 113, 0.12);
    background: #090D16 !important;
    color: #F8FAFC !important;
}

.st-key-sa-navbar {
    background: rgba(13, 18, 30, 0.92) !important;
    border-color: #1E293B !important;
    box-shadow: 0 2px 16px rgba(0, 0, 0, 0.4) !important;
}

.sa-brand-title { color: #F8FAFC !important; }
.sa-brand-icon {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(34, 211, 238, 0.15)) !important;
    border-color: rgba(99, 102, 241, 0.35) !important;
    color: #818CF8 !important;
}

/* Dark mode unselected pills */
.st-key-sa-navbar [data-testid="stPills"] button,
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pills"] {
    background: #172033 !important;
    border: 1px solid #1E293B !important;
    color: #94A3B8 !important;
}
.st-key-sa-navbar [data-testid="stPills"] button p,
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pills"] p,
.st-key-sa-navbar [data-testid="stPills"] button span,
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pills"] span {
    color: #94A3B8 !important;
}
.st-key-sa-navbar [data-testid="stPills"] button:hover,
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pills"]:hover {
    background: rgba(99, 102, 241, 0.16) !important;
    border-color: rgba(99, 102, 241, 0.35) !important;
    color: #818CF8 !important;
}
.st-key-sa-navbar [data-testid="stPills"] button:hover p,
.st-key-sa-navbar [data-testid="stPills"] button:hover span {
    color: #818CF8 !important;
}

/* Dark mode active pill */
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pillsActive"],
.st-key-sa-navbar [data-testid="stPills"] button[aria-checked="true"],
.st-key-sa-navbar [data-testid="stPills"] button[aria-selected="true"] {
    background: #6366F1 !important;
    border-color: #6366F1 !important;
    color: #FFFFFF !important;
    box-shadow: 0 2px 14px rgba(99, 102, 241, 0.45) !important;
}
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pillsActive"] p,
.st-key-sa-navbar [data-testid="stPills"] [data-testid="stBaseButton-pillsActive"] span,
.st-key-sa-navbar [data-testid="stPills"] button[aria-checked="true"] p,
.st-key-sa-navbar [data-testid="stPills"] button[aria-checked="true"] span,
.st-key-sa-navbar [data-testid="stPills"] button[aria-selected="true"] p,
.st-key-sa-navbar [data-testid="stPills"] button[aria-selected="true"] span {
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* Dark mode secondary buttons */
[data-testid="stBaseButton-secondary"],
.stButton > button:not([data-testid="stBaseButton-primary"]):not([data-testid="baseButton-primary"]) {
    background: #172033 !important;
    border: 1px solid #1E293B !important;
    color: #F8FAFC !important;
}
[data-testid="stBaseButton-secondary"]:hover,
.stButton > button:not([data-testid="stBaseButton-primary"]):not([data-testid="baseButton-primary"]):hover {
    border-color: #818CF8 !important;
    background: #1E293B !important;
    color: #818CF8 !important;
}

.st-key-theme_toggle button {
    background: #172033 !important;
    border-color: #1E293B !important;
    color: #F8FAFC !important;
}
.st-key-theme_toggle button:hover {
    border-color: #818CF8 !important;
    color: #818CF8 !important;
}

[data-testid="stVerticalBlockBorderWrapper"],
.metric-card, .kpi-card, .sa-footer {
    background: #111726 !important;
    border-color: #1E293B !important;
}

.metric-label, .kpi-lbl, .hero-desc, .page-subtitle, .section-sub,
.research-card-desc, .sa-footer-text, .metric-sub, .content-card-title, .card-header-bar {
    color: #64748B !important;
    border-color: #1E293B !important;
}
.metric-value, .kpi-val, .hero-title, .page-title, .section-title,
.research-card-title, .sa-footer-title {
    color: #F8FAFC !important;
}

.page-header { border-color: #1E293B !important; }
.kpi-icon, .metric-icon-wrap, .research-card-icon {
    background: rgba(99, 102, 241, 0.12) !important;
    border-color: rgba(99, 102, 241, 0.25) !important;
}
.dataset-badge {
    background: #172033 !important;
    border-color: #1E293B !important;
    color: #94A3B8 !important;
}
.hero-eyebrow {
    color: #818CF8 !important;
    background: rgba(99, 102, 241, 0.14) !important;
    border-color: rgba(99, 102, 241, 0.3) !important;
}
.grad-text {
    background: linear-gradient(135deg, #818CF8 0%, #22D3EE 100%) !important;
    -webkit-background-clip: text !important;
    background-clip: text !important;
    color: transparent !important;
    -webkit-text-fill-color: transparent !important;
}

[data-testid="stMetric"] { background: #111726 !important; border-color: #1E293B !important; }
[data-testid="stMetricLabel"] { color: #64748B !important; }
[data-testid="stMetricValue"] { color: #F8FAFC !important; }
[data-testid="stExpander"] { background: #111726 !important; border-color: #1E293B !important; }
[data-testid="stExpander"] summary { color: #F8FAFC !important; }
[data-testid="stDataFrame"] { border-color: #1E293B !important; }
[data-testid="stTabs"] [role="tablist"] { border-color: #1E293B !important; }
[data-testid="stTabs"] [role="tab"] { color: #94A3B8 !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: #818CF8 !important; border-bottom-color: #818CF8 !important; }
[data-testid="stSelectbox"] label, [data-testid="stMultiSelect"] label,
[data-testid="stSlider"] label, [data-testid="stRadio"] label { color: #94A3B8 !important; }
</style>
"""

# ── SVG brand icon ────────────────────────────────────────────────────────────
_DNA_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M2 15c6.667-6 13.333 0 20-6"/>'
    '<path d="M9 22c1.798-1.998 2.518-3.995 2.807-5.993"/>'
    '<path d="M15 2c-1.798 1.998-2.518 3.995-2.807 5.993"/>'
    '<path d="m17 6-2.5-2.5"/><path d="m14 8-1-1"/>'
    '<path d="m7 18 2.5 2.5"/><path d="m10 16 1 1"/>'
    '</svg>'
)


# ── HTML helpers ──────────────────────────────────────────────────────────────

def build_nav_html(active_page: str, dark: bool) -> str:
    """Kept for backwards compatibility."""
    return ""


def nav_brand_html() -> str:
    return (
        f'<div class="sa-brand">'
        f'<div class="sa-brand-icon">{_DNA_SVG}</div>'
        f'<div class="sa-brand-text">'
        f'<span class="sa-brand-title">Survival Analytics</span>'
        f'<span class="sa-brand-badge">RESEARCH</span>'
        f'</div>'
        f'</div>'
    )


def card_header_html(title: str, icon: str = "") -> str:
    icon_span = f'<span class="card-header-icon">{icon}</span>' if icon else ""
    return (
        f'<div class="card-header-bar">'
        f'{icon_span}'
        f'<span>{title}</span>'
        f'</div>'
    )


def metric_card_html(icon: str, label: str, value: str,
                     sub: str = "", synthetic: bool = False) -> str:
    badge = '<div class="synthetic-badge">&#9888; Synthetic data</div>' if synthetic else ""
    return (
        f'<div class="metric-card">'
        f'<div class="metric-icon-wrap">{icon}</div>'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-sub">{sub}</div>'
        f'{badge}'
        f'</div>'
    )


def kpi_card_html(value: str, label: str, icon: str = "") -> str:
    icon_html = (
        f'<div class="kpi-icon-row"><div class="kpi-icon">{icon}</div></div>'
        if icon else ""
    )
    return (
        f'<div class="kpi-card">'
        f'{icon_html}'
        f'<div class="kpi-val">{value}</div>'
        f'<div class="kpi-lbl">{label}</div>'
        f'</div>'
    )


def research_card_html(icon: str, title: str, desc: str) -> str:
    return (
        f'<div class="research-card-content">'
        f'<div class="research-card-icon">{icon}</div>'
        f'<div class="research-card-title">{title}</div>'
        f'<div class="research-card-desc">{desc}</div>'
        f'</div>'
    )


def page_header_html(title: str, subtitle: str = "", dataset_label: str = "") -> str:
    badge = ""
    if dataset_label:
        badge = (
            f'<div class="dataset-badge">'
            f'<span class="dataset-badge-dot"></span>'
            f'{dataset_label}'
            f'</div>'
        )
    return (
        f'<div class="page-header">'
        f'<div class="page-title">{title}</div>'
        f'<div class="page-subtitle">{subtitle}</div>'
        f'{badge}'
        f'</div>'
    )


def section_title_html(title: str, sub: str = "") -> str:
    return (
        f'<div class="section-title">{title}</div>'
        f'<div class="section-sub">{sub}</div>'
    )


def footer_html() -> str:
    return """
<div class="sa-footer">
  <div class="sa-footer-title">Survival Analytics · Clinical Biostatistics Platform</div>
  <div class="sa-footer-text">
    Comparative Statistical Analysis of Patient Survival Rates · Observational research tool.<br>
    Powered by Python, Streamlit, Lifelines, SciPy, Plotly &amp; ReportLab.<br>
    <strong>⚠ Synthetic data mode active — for demonstration and research prototyping.</strong>
  </div>
</div>
"""
