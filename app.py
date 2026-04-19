import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

st.set_page_config(page_title="Solar Panel Lab Graphs", layout="wide", page_icon="☀️")

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #f8f9fb; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { color: #1a1a2e; font-weight: 700; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: #fff; border-radius: 12px; padding: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); }
    .stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 20px; font-weight: 600; color: #555; }
    .stTabs [aria-selected="true"] { background: #1a73e8 !important; color: white !important; }
    .graph-card { background: white; border-radius: 16px; padding: 1.5rem; box-shadow: 0 4px 16px rgba(0,0,0,0.08); margin-bottom: 1.5rem; }
    .section-label { font-size: 0.78rem; font-weight: 600; color: #888; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 0.3rem; }
    .metric-row { display: flex; gap: 1.5rem; flex-wrap: wrap; margin: 1rem 0; }
    .metric-box { background: #f0f4ff; border-radius: 10px; padding: 0.7rem 1.2rem; flex: 1; min-width: 120px; }
    .metric-val { font-size: 1.3rem; font-weight: 700; color: #1a73e8; }
    .metric-lbl { font-size: 0.72rem; color: #666; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────────

# Table 1 – I-V Characteristics
panel1 = {
    "R":  [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0],
    "I":  [0.125, 0.130, 0.149, 0.164, 0.183, 0.209, 0.242, 0.281, 0.338, 0.390, 0.476],
    "V":  [18.5, 18.1, 18.0, 17.9, 17.8, 17.7, 17.6, 17.4, 16.9, 13.1, 0.4],
    "Wr": [64.01, 62.86, 62.66, 62.49, 62.36, 62.29, 62.15, 62.08, 61.93, 61.81, 61.72],
}
panel2 = {
    "R":  [100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0],
    "I":  [0.0]*11,
    "V":  [18.2]*11,
    "Wr": [65.08, 65.03, 65.00, 64.96, 64.91, 64.90, 64.88, 64.86, 64.84, 64.82, 64.81],
}

# Table 2 – Voc vs Temperature
vent_on = {
    "SUN": [0,10,20,30,40,50,60,70,80,90,100],
    "V":   [1.2,1.3,9.5,14.8,16.6,17.84,18.0,18.3,18.6,18.7,18.7],
    "ST2": [28.4,27.8,27.8,27.8,27.9,27.9,28.1,28.5,28.6,28.9,29.1],
    "Wr":  [0.0,0.0,36.47,51.74,59.05,62.88,64.85,65.88,66.40,66.60,66.53],
}
vent_off = {
    "SUN": [0,10,20,30,40,50,60,70,80,90,100],
    "V":   [1.1,1.3,9.2,14.6,16.3,17.4,17.9,18.3,18.5,18.6,18.6],
    "ST2": [30.7,31.0,31.1,31.2,31.4,31.6,31.9,32.3,32.9,33.5,34.2],
    "Wr":  [0.0,0.0,35.08,50.85,58.45,62.40,64.45,65.45,65.90,66.0,65.90],
}

# ─── PLOT HELPERS ─────────────────────────────────────────────────────────────

def style_axes(ax, xlabel, ylabel, title):
    ax.set_xlabel(xlabel, fontsize=11, fontweight='600', color='#333', labelpad=10)
    ax.set_ylabel(ylabel, fontsize=11, fontweight='600', color='#333', labelpad=10)
    ax.set_title(title, fontsize=13, fontweight='700', color='#1a1a2e', pad=16)
    ax.spines[['top','right']].set_visible(False)
    ax.spines[['left','bottom']].set_color('#ccc')
    ax.tick_params(colors='#555', labelsize=9)
    ax.grid(axis='both', linestyle='--', linewidth=0.5, color='#ddd', alpha=0.8)
    ax.set_facecolor('#fafbff')

def annotate_wr(ax, xs, ys, wrs, color, offset=(4, 6)):
    for x, y, wr in zip(xs, ys, wrs):
        if wr > 0:
            ax.annotate(
                f"{wr:.1f} W/m²",
                xy=(x, y), xytext=(offset[0], offset[1]),
                textcoords='offset points',
                fontsize=6.5, color=color, alpha=0.85,
                arrowprops=dict(arrowstyle='-', color=color, alpha=0.4, lw=0.5),
            )

# ─── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("## ☀️ Solar Panel Lab — Characteristic Graphs")
st.markdown("<p style='color:#888;margin-top:-0.5rem;font-size:0.9rem;'>Emmanuel Bachopi & Kaone Kopelo · Determination of Solar Panel Parameters</p>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2 = st.tabs(["📈  I-V Curves (Table 1)", "🌡️  Voc–Temperature Curves (Table 2)"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 – I-V CURVES
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    col_info, _ = st.columns([3,1])
    with col_info:
        st.markdown("#### I–V Characteristic Curves")
        st.markdown(
            "<p style='color:#555;font-size:0.88rem;'>Current (I) vs Voltage (V) for Panel-1 and Panel-2 at varying load resistance. "
            "Solar radiation (W<sub>r</sub>) is labelled at every measured point.</p>",
            unsafe_allow_html=True,
        )

    # ── Key metrics ──
    isc1 = max(panel1["I"]); voc1 = max(panel1["V"]); pmax1 = max(i*v for i,v in zip(panel1["I"],panel1["V"]))
    st.markdown(f"""
    <div class='metric-row'>
      <div class='metric-box'><div class='metric-val'>{isc1:.3f} A</div><div class='metric-lbl'>Panel-1  Isc (short-circuit)</div></div>
      <div class='metric-box'><div class='metric-val'>{voc1:.1f} V</div><div class='metric-lbl'>Panel-1  Voc (open-circuit)</div></div>
      <div class='metric-box'><div class='metric-val'>{pmax1:.3f} W</div><div class='metric-lbl'>Panel-1  Pmax (est.)</div></div>
      <div class='metric-box'><div class='metric-val'>18.2 V</div><div class='metric-lbl'>Panel-2  Voc (constant)</div></div>
    </div>
    """, unsafe_allow_html=True)

    colA, colB = st.columns(2)

    # ── Graph 1: Panel-1 I-V ──
    with colA:
        st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
        fig1, ax1 = plt.subplots(figsize=(6.5, 4.8))
        fig1.patch.set_facecolor('white')

        c1 = '#1a73e8'
        ax1.plot(panel1["V"], panel1["I"], color=c1, linewidth=2.2, zorder=3)
        ax1.scatter(panel1["V"], panel1["I"], color=c1, s=45, zorder=4)
        annotate_wr(ax1, panel1["V"], panel1["I"], panel1["Wr"], color='#555', offset=(5, 7))

        # Dotted reference lines for Voc and Isc
        ax1.axhline(y=max(panel1["I"]), color='#aaa', linestyle=':', linewidth=1)
        ax1.axvline(x=max(panel1["V"]), color='#aaa', linestyle=':', linewidth=1)
        ax1.text(max(panel1["V"])+0.1, 0.02, f'Voc={max(panel1["V"])}V', fontsize=7.5, color='#888')
        ax1.text(0.5, max(panel1["I"])+0.005, f'Isc={max(panel1["I"])}A', fontsize=7.5, color='#888')

        style_axes(ax1, "Voltage, V (Volts)", "Current, I (Amperes)", "Graph 1 – Panel-1: I-V Curve")
        ax1.set_xlim(-0.5, 20); ax1.set_ylim(-0.02, 0.55)
        fig1.tight_layout()
        st.pyplot(fig1, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Graph 2: Panel-2 I-V ──
    with colB:
        st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(6.5, 4.8))
        fig2.patch.set_facecolor('white')

        c2 = '#e05c00'
        ax2.plot(panel2["V"], panel2["I"], color=c2, linewidth=2.2, zorder=3)
        ax2.scatter(panel2["V"], panel2["I"], color=c2, s=45, zorder=4, label='Data points')

        # Annotate Wr – since all V values are the same (18.2), stagger labels vertically
        for k, (x, y, wr) in enumerate(zip(panel2["V"], panel2["I"], panel2["Wr"])):
            ax2.annotate(
                f"{wr:.2f} W/m²",
                xy=(x, y),
                xytext=(-60 + k*3, 20 + k*12),
                textcoords='offset points',
                fontsize=6.5, color='#555', alpha=0.85,
                arrowprops=dict(arrowstyle='-', color='#aaa', alpha=0.5, lw=0.5),
            )

        ax2.axvline(x=18.2, color='#aaa', linestyle=':', linewidth=1)
        ax2.text(18.25, 0.02, 'Voc = 18.2V', fontsize=7.5, color='#888')
        ax2.text(14, 0.06, 'Isc not measured\n(I = 0 A at all positions)', fontsize=8.5,
                 color='#c0392b', ha='center',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='#fff5f5', edgecolor='#f5c6c6'))

        style_axes(ax2, "Voltage, V (Volts)", "Current, I (Amperes)", "Graph 2 – Panel-2: I-V Curve")
        ax2.set_xlim(15, 20); ax2.set_ylim(-0.05, 0.6)
        fig2.tight_layout()
        st.pyplot(fig2, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Graph overlay / compare ──
    st.markdown("#### Panel-1 vs Panel-2 — Overlay")
    st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
    fig3, ax3 = plt.subplots(figsize=(10, 4.5))
    fig3.patch.set_facecolor('white')
    ax3.plot(panel1["V"], panel1["I"], color='#1a73e8', linewidth=2.2, label='Panel-1', marker='o', markersize=5)
    ax3.plot(panel2["V"], panel2["I"], color='#e05c00', linewidth=2.2, label='Panel-2', marker='s', markersize=5)
    style_axes(ax3, "Voltage, V (Volts)", "Current, I (Amperes)", "Graph 1 & 2 — Panel-1 vs Panel-2: I-V Overlay")
    ax3.legend(fontsize=10, framealpha=0.9)
    ax3.set_xlim(-0.5, 20); ax3.set_ylim(-0.05, 0.6)
    fig3.tight_layout()
    st.pyplot(fig3, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 – Voc-T CURVES
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    col_info2, _ = st.columns([3,1])
    with col_info2:
        st.markdown("#### V<sub>oc</sub>–Temperature (ST-2) Graphs", unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#555;font-size:0.88rem;'>Open-circuit voltage (V<sub>oc</sub>) vs Panel temperature (ST-2 sensor) "
            "with ventilation ON and OFF. Solar radiation (W<sub>r</sub>) is labelled at every point.</p>",
            unsafe_allow_html=True,
        )

    colC, colD = st.columns(2)

    # ── Graph 3: Voc vs T – Ventilation ON ──
    with colC:
        st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
        fig4, ax4 = plt.subplots(figsize=(6.5, 4.8))
        fig4.patch.set_facecolor('white')

        c3 = '#0f9d58'
        ax4.plot(vent_on["ST2"], vent_on["V"], color=c3, linewidth=2.2, zorder=3)
        ax4.scatter(vent_on["ST2"], vent_on["V"], color=c3, s=45, zorder=4)

        # Annotate Wr at each point
        for k, (x, y, wr) in enumerate(zip(vent_on["ST2"], vent_on["V"], vent_on["Wr"])):
            label = f"{wr:.2f} W/m²" if wr > 0 else "Wr = 0"
            offset_x = 5 if k % 2 == 0 else -68
            offset_y = 6 if k < 5 else -14
            ax4.annotate(label, xy=(x, y), xytext=(offset_x, offset_y),
                         textcoords='offset points', fontsize=6.5, color='#444', alpha=0.9,
                         arrowprops=dict(arrowstyle='-', color='#aaa', alpha=0.5, lw=0.5))

        # Dotted max Voc line
        ax4.axhline(y=max(vent_on["V"]), color='#aaa', linestyle=':', linewidth=1)
        ax4.text(28.42, max(vent_on["V"])+0.2, f'Voc max = {max(vent_on["V"])} V', fontsize=7.5, color='#888')

        style_axes(ax4, "Temperature, ST-2 (°C)", "Open-Circuit Voltage, Voc (V)",
                   "Graph 3 – Ventilation ON: Voc vs Temperature")
        ax4.set_xlim(27.5, 29.5); ax4.set_ylim(-0.5, 21)
        fig4.tight_layout()
        st.pyplot(fig4, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Graph 4: Voc vs T – Ventilation OFF ──
    with colD:
        st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
        fig5, ax5 = plt.subplots(figsize=(6.5, 4.8))
        fig5.patch.set_facecolor('white')

        c4 = '#d62d20'
        ax5.plot(vent_off["ST2"], vent_off["V"], color=c4, linewidth=2.2, zorder=3)
        ax5.scatter(vent_off["ST2"], vent_off["V"], color=c4, s=45, zorder=4)

        for k, (x, y, wr) in enumerate(zip(vent_off["ST2"], vent_off["V"], vent_off["Wr"])):
            label = f"{wr:.2f} W/m²" if wr > 0 else "Wr = 0"
            offset_x = 5 if k % 2 == 0 else -68
            offset_y = 6 if k < 5 else -14
            ax5.annotate(label, xy=(x, y), xytext=(offset_x, offset_y),
                         textcoords='offset points', fontsize=6.5, color='#444', alpha=0.9,
                         arrowprops=dict(arrowstyle='-', color='#aaa', alpha=0.5, lw=0.5))

        ax5.axhline(y=max(vent_off["V"]), color='#aaa', linestyle=':', linewidth=1)
        ax5.text(30.72, max(vent_off["V"])+0.2, f'Voc max = {max(vent_off["V"])} V', fontsize=7.5, color='#888')

        style_axes(ax5, "Temperature, ST-2 (°C)", "Open-Circuit Voltage, Voc (V)",
                   "Graph 4 – Ventilation OFF: Voc vs Temperature")
        ax5.set_xlim(30.4, 34.5); ax5.set_ylim(-0.5, 21)
        fig5.tight_layout()
        st.pyplot(fig5, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Overlay Graph 3 & 4 ──
    st.markdown("#### Ventilation ON vs OFF — Overlay")
    st.markdown("<div class='graph-card'>", unsafe_allow_html=True)
    fig6, ax6 = plt.subplots(figsize=(10, 4.5))
    fig6.patch.set_facecolor('white')
    ax6.plot(vent_on["ST2"], vent_on["V"], color='#0f9d58', linewidth=2.2,
             label='Ventilation ON', marker='o', markersize=5)
    ax6.plot(vent_off["ST2"], vent_off["V"], color='#d62d20', linewidth=2.2,
             label='Ventilation OFF', marker='s', markersize=5)

    # Label sun positions
    for x, y, sun in zip(vent_on["ST2"], vent_on["V"], vent_on["SUN"]):
        ax6.annotate(f"SUN {sun}%", xy=(x, y), xytext=(0, 8), textcoords='offset points',
                     fontsize=6, color='#0f9d58', ha='center')
    for x, y, sun in zip(vent_off["ST2"], vent_off["V"], vent_off["SUN"]):
        ax6.annotate(f"SUN {sun}%", xy=(x, y), xytext=(0, -14), textcoords='offset points',
                     fontsize=6, color='#d62d20', ha='center')

    style_axes(ax6, "Temperature, ST-2 (°C)", "Open-Circuit Voltage, Voc (V)",
               "Graph 3 & 4 — Ventilation ON vs OFF: Voc vs Temperature Overlay")
    ax6.legend(fontsize=10, framealpha=0.9)
    fig6.tight_layout()
    st.pyplot(fig6, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#aaa;font-size:0.78rem;'>"
    "Determination of Solar Panel Parameters & Influence of Temperature on Open-Circuit Voltage · Lab Report</p>",
    unsafe_allow_html=True,
)
