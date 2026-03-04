import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tableau de Bord", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f9fafb; color: #111827; }

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e5e7eb;
}

h1 {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
    color: #111827 !important;
    margin-bottom: 0 !important;
}
h2 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #374151 !important;
    margin: 0 !important;
}

/* Nav buttons */
div[data-testid="stHorizontalBlock"] > div > div > button {
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    transition: all 0.15s;
}

[data-testid="metric-container"] {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 14px 18px !important;
}
[data-testid="metric-container"] label {
    color: #6b7280 !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 500 !important;
}
[data-testid="metric-container"] [data-testid="metric-value"] {
    color: #111827 !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
}

.card-title {
    font-size: 0.72rem;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
}
.winner-banner-green {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 16px 22px;
    margin-bottom: 16px;
}
.winner-banner-yellow {
    background: #fefce8;
    border: 1px solid #fde68a;
    border-radius: 8px;
    padding: 16px 22px;
    margin-bottom: 16px;
}
.winner-name-green { font-size: 1.2rem; font-weight: 700; color: #15803d; }
.winner-name-yellow { font-size: 1.2rem; font-weight: 700; color: #92400e; }
.winner-sub { font-size: 0.82rem; color: #4b5563; margin-top: 3px; }

.sidebar-label {
    font-size: 0.68rem;
    font-weight: 600;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 14px 0 4px;
}
[data-testid="stDataFrame"] { border: 1px solid #e5e7eb; border-radius: 8px; }
hr { border: none; border-top: 1px solid #e5e7eb !important; margin: 20px 0 !important; }

/* Active nav pill */
.nav-active {
    background: #111827;
    color: #ffffff;
    border-radius: 6px;
    padding: 6px 18px;
    font-weight: 600;
    font-size: 0.85rem;
    display: inline-block;
}
.nav-inactive {
    background: #f3f4f6;
    color: #6b7280;
    border-radius: 6px;
    padding: 6px 18px;
    font-weight: 500;
    font-size: 0.85rem;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# ── Palette & theme ───────────────────────────────────────────────────────────
C = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4", "#f97316"]

def th(fig, legend=False):
    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#374151", size=12),
        margin=dict(l=8, r=8, t=40, b=8),
        colorway=C,
        showlegend=legend,
        legend=dict(
            bgcolor="#ffffff",
            bordercolor="#e5e7eb",
            borderwidth=1,
            font=dict(size=11, color="#374151"),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ) if legend else {},
        title_font=dict(size=13, color="#374151", family="Inter"),
    )
    fig.update_xaxes(
        gridcolor="#f3f4f6", linecolor="#e5e7eb",
        tickfont=dict(size=11, color="#6b7280"), title_font=dict(size=11),
    )
    fig.update_yaxes(
        gridcolor="#f3f4f6", linecolor="#e5e7eb",
        tickfont=dict(size=11, color="#6b7280"), title_font=dict(size=11),
    )
    return fig

# ── Data loaders ──────────────────────────────────────────────────────────────
@st.cache_data
def load_ventes():
    df = pd.read_excel("cleaned_ventes.xlsx")
    df["date_cmd"] = pd.to_datetime(df["date_cmd"])
    df["annee"]    = df["date_cmd"].dt.year.astype(str)
    df["mois_ts"]  = df["date_cmd"].dt.to_period("M").dt.to_timestamp()
    return df

@st.cache_data
def load_achats():
    df = pd.read_csv("achats_clean.csv", parse_dates=["date_cmd"])
    df["annee"]   = df["date_cmd"].dt.year.astype(str)
    df["mois_ts"] = df["date_cmd"].dt.to_period("M").dt.to_timestamp()
    return df

@st.cache_data
def load_marges():
    ventes = pd.read_excel("cleaned_ventes.xlsx")
    ventes["date_cmd"] = pd.to_datetime(ventes["date_cmd"])
    ventes["pu_vente"] = ventes["montant_ht"] / ventes["qte"]

    achats = pd.read_csv("achats_clean.csv", parse_dates=["date_cmd"])
    achats["pu_achat"] = achats["montant_ht"] / achats["qte"]

    pu_achat_avg = (
        achats.sort_values("date_cmd")
        .groupby("code_produit")["pu_achat"]
        .first().reset_index()
        .rename(columns={"pu_achat": "pu_achat_moy"})
    )
    # INK.0004 same product as INK.0034
    if "INK.0004" not in pu_achat_avg["code_produit"].values:
        p = pu_achat_avg.loc[pu_achat_avg["code_produit"] == "INK.0034", "pu_achat_moy"].values
        if len(p) > 0:
            pu_achat_avg = pd.concat([
                pu_achat_avg,
                pd.DataFrame([{"code_produit": "INK.0004", "pu_achat_moy": p[0]}])
            ], ignore_index=True)

    df = ventes.merge(pu_achat_avg, on="code_produit", how="left")
    df["marge_unitaire"] = df["pu_vente"] - df["pu_achat_moy"]
    df["marge_totale"]   = df["marge_unitaire"] * df["qte"]
    df["taux_marge_pct"] = (df["marge_unitaire"] / df["pu_vente"] * 100).round(1)
    df["annee"]   = df["date_cmd"].dt.year.astype(str)
    df["mois_ts"] = df["date_cmd"].dt.to_period("M").dt.to_timestamp()
    return df

# ── Navigation state ──────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Ventes"

# ── Top navigation bar ────────────────────────────────────────────────────────
st.markdown("# Tableau de Bord")
st.markdown("<hr>", unsafe_allow_html=True)

n1, n2, n3, _ = st.columns([1, 1, 1, 5])
with n1:
    if st.button("Ventes", use_container_width=True,
                 type="primary" if st.session_state.page == "Ventes" else "secondary"):
        st.session_state.page = "Ventes"
        st.rerun()
with n2:
    if st.button("Achats", use_container_width=True,
                 type="primary" if st.session_state.page == "Achats" else "secondary"):
        st.session_state.page = "Achats"
        st.rerun()
with n3:
    if st.button("Marges", use_container_width=True,
                 type="primary" if st.session_state.page == "Marges" else "secondary"):
        st.session_state.page = "Marges"
        st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — VENTES
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "Ventes":
    df = load_ventes()
    CUTOFF = pd.Timestamp("2025-02-01")

    with st.sidebar:
        st.markdown("**Filtres — Ventes**")
        st.markdown("<div class='sidebar-label'>Période</div>", unsafe_allow_html=True)
        min_d = df["date_cmd"].min().date()
        max_d = df["date_cmd"].max().date()
        d_from = st.date_input("Du", value=min_d, min_value=min_d, max_value=max_d, key="v_from")
        d_to   = st.date_input("Au", value=max_d, min_value=min_d, max_value=max_d, key="v_to")
        if d_from > d_to:
            st.error("La date de début doit être avant la date de fin.")
            d_from, d_to = min_d, max_d
        st.markdown("<div class='sidebar-label'>Données</div>", unsafe_allow_html=True)
        types   = st.multiselect("Type de vente", df["type_vente"].unique().tolist(),
                                 default=df["type_vente"].unique().tolist(), key="v_types")
        cats    = st.multiselect("Catégorie", df["categorie_produit"].unique().tolist(),
                                 default=df["categorie_produit"].unique().tolist(), key="v_cats")
        wilayas = st.multiselect("Wilaya", df["wilaya"].unique().tolist(),
                                 default=df["wilaya"].unique().tolist(), key="v_wil")
        st.markdown("---")
        if st.button("Réinitialiser", use_container_width=True, key="v_reset"):
            st.rerun()
        st.caption("Le filtre date ne s'applique pas à la section « Produits après 01/02/2025 ».")

    mask = (
        (df["date_cmd"].dt.date >= d_from) & (df["date_cmd"].dt.date <= d_to) &
        df["type_vente"].isin(types) & df["categorie_produit"].isin(cats) & df["wilaya"].isin(wilayas)
    )
    dff = df[mask].copy()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("CA Total TTC",   f"{dff['montant_ttc'].sum():,.0f} DA")
    k2.metric("Commandes",       dff["num_cmd"].nunique())
    k3.metric("Clients",         dff["client"].nunique())
    k4.metric("Quantité Vendue", f"{dff['qte'].sum():,}")
    k5.metric("Produits",        dff["produit"].nunique())
    st.markdown("<hr>", unsafe_allow_html=True)

    if dff.empty:
        st.warning("Aucune donnée pour les filtres sélectionnés.")
        st.stop()

    # 1
    st.markdown("## Produits vendus après le 01 Février 2025")
    df_after = df[df["date_cmd"] > CUTOFF]
    c1, c2 = st.columns([1.3, 1], gap="large")
    with c1:
        st.markdown("<div class='card-title'>Liste des produits</div>", unsafe_allow_html=True)
        st.dataframe(
            df_after[["date_cmd","client","produit","categorie_produit","type_vente","qte","montant_ttc"]]
            .rename(columns={"date_cmd":"Date","client":"Client","produit":"Produit",
                             "categorie_produit":"Catégorie","type_vente":"Type",
                             "qte":"Qté","montant_ttc":"TTC (DA)"}),
            use_container_width=True, hide_index=True)
    with c2:
        ca_after = df_after.groupby("produit")["montant_ttc"].sum().reset_index().sort_values("montant_ttc", ascending=True)
        fig = px.bar(ca_after, x="montant_ttc", y="produit", orientation="h",
                     color_discrete_sequence=[C[0]],
                     labels={"montant_ttc":"CA TTC (DA)","produit":""}, title="CA par produit")
        th(fig); st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 2
    st.markdown("## Classement des produits par Chiffre d'Affaires")
    c3, c4 = st.columns(2, gap="large")
    with c3:
        ca_type = dff.groupby(["produit","type_vente"])["montant_ttc"].sum().reset_index()
        fig2 = px.bar(ca_type, x="produit", y="montant_ttc", color="type_vente", barmode="group",
                      color_discrete_sequence=C,
                      labels={"montant_ttc":"CA TTC (DA)","produit":"","type_vente":"Type"},
                      title="CA par produit et type de vente")
        fig2.update_xaxes(tickangle=-20); th(fig2, legend=True); st.plotly_chart(fig2, use_container_width=True)
    with c4:
        ca_yr = dff.groupby(["produit","annee"])["montant_ttc"].sum().reset_index()
        fig3 = px.bar(ca_yr, x="produit", y="montant_ttc", color="annee", barmode="group",
                      color_discrete_sequence=C,
                      labels={"montant_ttc":"CA TTC (DA)","produit":"","annee":"Année"},
                      title="CA par produit et année")
        fig3.update_xaxes(tickangle=-20); th(fig3, legend=True); st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 3
    st.markdown("## Classement des clients")
    client_agg = (dff.groupby(["client","wilaya","forme_juridique"])
                  .agg(ca=("montant_ttc","sum"), nb=("num_cmd","nunique"))
                  .reset_index().sort_values("ca", ascending=False))
    c5, c6, c7 = st.columns([1.4, 1, 1], gap="large")
    with c5:
        fig4 = px.bar(client_agg.sort_values("ca", ascending=True),
                      x="ca", y="client", color="wilaya", orientation="h",
                      color_discrete_sequence=C,
                      labels={"ca":"CA TTC (DA)","client":"","wilaya":"Wilaya"},
                      title="CA par client et wilaya")
        th(fig4, legend=True); st.plotly_chart(fig4, use_container_width=True)
    with c6:
        w_agg = dff.groupby("wilaya")["montant_ttc"].sum().reset_index()
        fig5 = px.pie(w_agg, values="montant_ttc", names="wilaya", hole=0.5,
                      color_discrete_sequence=C, title="CA par wilaya")
        fig5.update_traces(textinfo="percent+label", textposition="outside")
        th(fig5, legend=False); st.plotly_chart(fig5, use_container_width=True)
    with c7:
        fj_agg = dff.groupby("forme_juridique")["montant_ttc"].sum().reset_index()
        fig6 = px.pie(fj_agg, values="montant_ttc", names="forme_juridique", hole=0.5,
                      color_discrete_sequence=C, title="CA par forme juridique")
        fig6.update_traces(textinfo="percent+label", textposition="outside")
        th(fig6, legend=False); st.plotly_chart(fig6, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 4
    st.markdown("## Ventes quantitatives")
    c8, c9 = st.columns(2, gap="large")
    with c8:
        qte_type = dff.groupby(["produit","type_vente"])["qte"].sum().reset_index()
        fig7 = px.bar(qte_type, x="produit", y="qte", color="type_vente", barmode="stack",
                      color_discrete_sequence=C,
                      labels={"qte":"Quantité","produit":"","type_vente":"Type"},
                      title="Quantité par produit et type de vente")
        fig7.update_xaxes(tickangle=-20); th(fig7, legend=True); st.plotly_chart(fig7, use_container_width=True)
    with c9:
        qte_cat_yr = dff.groupby(["categorie_produit","annee"])["qte"].sum().reset_index()
        fig8 = px.bar(qte_cat_yr, x="categorie_produit", y="qte", color="annee", barmode="group",
                      color_discrete_sequence=C,
                      labels={"qte":"Quantité","categorie_produit":"","annee":"Année"},
                      title="Quantité par catégorie et année")
        th(fig8, legend=True); st.plotly_chart(fig8, use_container_width=True)

    qte_m = dff.groupby(["mois_ts","categorie_produit"])["qte"].sum().reset_index().sort_values("mois_ts")
    fig9 = px.line(qte_m, x="mois_ts", y="qte", color="categorie_produit",
                   markers=True, color_discrete_sequence=C,
                   labels={"qte":"Quantité","mois_ts":"Mois","categorie_produit":"Catégorie"},
                   title="Evolution mensuelle des quantités par catégorie")
    fig9.update_traces(line_width=2, marker_size=7); th(fig9, legend=True); st.plotly_chart(fig9, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 5
    st.markdown("## Catégorie la plus rentable")
    cat_agg = (dff.groupby("categorie_produit")
               .agg(ca_ttc=("montant_ttc","sum"), qte=("qte","sum"))
               .reset_index().sort_values("ca_ttc", ascending=False))
    winner = cat_agg.iloc[0]["categorie_produit"]
    w_ttc  = cat_agg.iloc[0]["ca_ttc"]
    pct    = w_ttc / cat_agg["ca_ttc"].sum() * 100
    st.markdown(f"""<div class='winner-banner-green'>
      <div><div class='winner-name-green'>{winner}</div>
      <div class='winner-sub'>CA TTC : <b>{w_ttc:,.0f} DA</b> &nbsp;·&nbsp; Part du total : <b>{pct:.1f}%</b></div>
      </div></div>""", unsafe_allow_html=True)
    c10, c11 = st.columns(2, gap="large")
    with c10:
        fig10 = px.bar(cat_agg.sort_values("ca_ttc"), x="ca_ttc", y="categorie_produit",
                       orientation="h", color="categorie_produit", color_discrete_sequence=C,
                       labels={"ca_ttc":"CA TTC (DA)","categorie_produit":""}, title="CA TTC par catégorie")
        th(fig10, legend=False); st.plotly_chart(fig10, use_container_width=True)
    with c11:
        fig11 = px.pie(cat_agg, values="ca_ttc", names="categorie_produit", hole=0.55,
                       color_discrete_sequence=C, title="Part du CA par catégorie")
        fig11.update_traces(textinfo="percent+label", textposition="outside",
                            pull=[0.06 if i == 0 else 0 for i in range(len(cat_agg))])
        th(fig11, legend=False); st.plotly_chart(fig11, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — ACHATS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Achats":
    df = load_achats()

    with st.sidebar:
        st.markdown("**Filtres — Achats**")
        st.markdown("<div class='sidebar-label'>Période</div>", unsafe_allow_html=True)
        min_d = df["date_cmd"].min().date()
        max_d = df["date_cmd"].max().date()
        d_from = st.date_input("Du", value=min_d, min_value=min_d, max_value=max_d, key="a_from")
        d_to   = st.date_input("Au", value=max_d, min_value=min_d, max_value=max_d, key="a_to")
        if d_from > d_to:
            st.error("La date de début doit être avant la date de fin.")
            d_from, d_to = min_d, max_d
        st.markdown("<div class='sidebar-label'>Données</div>", unsafe_allow_html=True)
        types = st.multiselect("Type d'achat", df["type_achat"].unique().tolist(),
                               default=df["type_achat"].unique().tolist(), key="a_types")
        cats  = st.multiselect("Catégorie", df["categorie_produit"].unique().tolist(),
                               default=df["categorie_produit"].unique().tolist(), key="a_cats")
        fourn = st.multiselect("Fournisseur", df["fournisseur"].unique().tolist(),
                               default=df["fournisseur"].unique().tolist(), key="a_fourn")
        st.markdown("---")
        if st.button("Réinitialiser", use_container_width=True, key="a_reset"):
            st.rerun()
        st.caption("Le filtre date ne s'applique pas à la section « Produits 2024 ».")

    mask = (
        (df["date_cmd"].dt.date >= d_from) & (df["date_cmd"].dt.date <= d_to) &
        df["type_achat"].isin(types) & df["categorie_produit"].isin(cats) & df["fournisseur"].isin(fourn)
    )
    dff = df[mask].copy()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Coût Total TTC",   f"{dff['montant_ttc'].sum():,.0f} DA")
    k2.metric("Coût Total HT",    f"{dff['montant_ht'].sum():,.0f} DA")
    k3.metric("Bons de Commande", dff["num_cmd"].nunique())
    k4.metric("Quantité Achetée", f"{dff['qte'].sum():,}")
    k5.metric("Fournisseurs",     dff["fournisseur"].nunique())
    st.markdown("<hr>", unsafe_allow_html=True)

    if dff.empty:
        st.warning("Aucune donnée pour les filtres sélectionnés.")
        st.stop()

    # 1
    st.markdown("## Produits achetés en 2024")
    df24 = df[df["annee"] == "2024"].copy()
    c1, c2 = st.columns([1.4, 1], gap="large")
    with c1:
        st.markdown("<div class='card-title'>Liste des produits</div>", unsafe_allow_html=True)
        st.dataframe(
            df24[["date_cmd","fournisseur","produit","categorie_produit","type_achat","qte","montant_ttc"]]
            .rename(columns={"date_cmd":"Date","fournisseur":"Fournisseur","produit":"Produit",
                             "categorie_produit":"Catégorie","type_achat":"Type",
                             "qte":"Qté","montant_ttc":"TTC (DA)"}),
            use_container_width=True, hide_index=True)
    with c2:
        prod24 = df24.groupby("produit")["montant_ttc"].sum().reset_index().sort_values("montant_ttc", ascending=True)
        fig1 = px.bar(prod24, x="montant_ttc", y="produit", orientation="h",
                      color_discrete_sequence=[C[0]],
                      labels={"montant_ttc":"Coût TTC (DA)","produit":""}, title="Coût par produit (2024)")
        th(fig1); st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 2
    st.markdown("## Achats quantitatifs")
    c3, c4 = st.columns(2, gap="large")
    with c3:
        qte_type = dff.groupby(["produit","type_achat"])["qte"].sum().reset_index()
        fig2 = px.bar(qte_type, x="produit", y="qte", color="type_achat", barmode="group",
                      color_discrete_sequence=C,
                      labels={"qte":"Quantité","produit":"","type_achat":"Type"},
                      title="Quantité par produit et type d'achat")
        fig2.update_xaxes(tickangle=-20); th(fig2, legend=True); st.plotly_chart(fig2, use_container_width=True)
    with c4:
        qte_yr = dff.groupby(["produit","annee"])["qte"].sum().reset_index()
        fig3 = px.bar(qte_yr, x="produit", y="qte", color="annee", barmode="group",
                      color_discrete_sequence=C,
                      labels={"qte":"Quantité","produit":"","annee":"Année"},
                      title="Quantité par produit et année")
        fig3.update_xaxes(tickangle=-20); th(fig3, legend=True); st.plotly_chart(fig3, use_container_width=True)

    qte_m = dff.groupby(["mois_ts","categorie_produit"])["qte"].sum().reset_index().sort_values("mois_ts")
    fig4 = px.line(qte_m, x="mois_ts", y="qte", color="categorie_produit",
                   markers=True, color_discrete_sequence=C,
                   labels={"qte":"Quantité","mois_ts":"Mois","categorie_produit":"Catégorie"},
                   title="Evolution mensuelle des quantités par catégorie")
    fig4.update_traces(line_width=2, marker_size=7); th(fig4, legend=True); st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 3
    st.markdown("## Classement des fournisseurs")
    fourn_agg = (dff.groupby(["fournisseur","categorie_produit"])
                 .agg(montant_ttc=("montant_ttc","sum"), qte=("qte","sum"))
                 .reset_index().sort_values("montant_ttc", ascending=False))
    c5, c6, c7 = st.columns([1.4, 1, 1], gap="large")
    with c5:
        fig5 = px.bar(fourn_agg.sort_values("montant_ttc", ascending=True),
                      x="montant_ttc", y="fournisseur", color="categorie_produit",
                      orientation="h", barmode="stack", color_discrete_sequence=C,
                      labels={"montant_ttc":"Coût TTC (DA)","fournisseur":"","categorie_produit":"Catégorie"},
                      title="Coût par fournisseur et catégorie")
        th(fig5, legend=True); st.plotly_chart(fig5, use_container_width=True)
    with c6:
        ft = dff.groupby("fournisseur")["montant_ttc"].sum().reset_index()
        fig6 = px.pie(ft, values="montant_ttc", names="fournisseur", hole=0.5,
                      color_discrete_sequence=C, title="Part du coût par fournisseur")
        fig6.update_traces(textinfo="percent+label", textposition="outside")
        th(fig6, legend=False); st.plotly_chart(fig6, use_container_width=True)
    with c7:
        fig7 = px.bar(fourn_agg.sort_values("qte", ascending=True),
                      x="qte", y="fournisseur", color="categorie_produit",
                      orientation="h", barmode="stack", color_discrete_sequence=C,
                      labels={"qte":"Quantité","fournisseur":"","categorie_produit":"Catégorie"},
                      title="Quantité par fournisseur et catégorie")
        th(fig7, legend=True); st.plotly_chart(fig7, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 4
    st.markdown("## Catégorie la plus coûteuse")
    cat_agg = (dff.groupby("categorie_produit")
               .agg(montant_ttc=("montant_ttc","sum"), qte=("qte","sum"))
               .reset_index().sort_values("montant_ttc", ascending=False))
    winner = cat_agg.iloc[0]["categorie_produit"]
    w_ttc  = cat_agg.iloc[0]["montant_ttc"]
    pct    = w_ttc / cat_agg["montant_ttc"].sum() * 100
    st.markdown(f"""<div class='winner-banner-yellow'>
      <div><div class='winner-name-yellow'>{winner}</div>
      <div class='winner-sub'>Coût TTC : <b>{w_ttc:,.0f} DA</b> &nbsp;·&nbsp; Part du total : <b>{pct:.1f}%</b></div>
      </div></div>""", unsafe_allow_html=True)
    c8, c9 = st.columns(2, gap="large")
    with c8:
        fig8 = px.bar(cat_agg.sort_values("montant_ttc"), x="montant_ttc", y="categorie_produit",
                      orientation="h", color="categorie_produit", color_discrete_sequence=C,
                      labels={"montant_ttc":"Coût TTC (DA)","categorie_produit":""}, title="Coût TTC par catégorie")
        th(fig8, legend=False); st.plotly_chart(fig8, use_container_width=True)
    with c9:
        fig9 = px.pie(cat_agg, values="montant_ttc", names="categorie_produit", hole=0.55,
                      color_discrete_sequence=C, title="Répartition du coût par catégorie")
        fig9.update_traces(textinfo="percent+label", textposition="outside",
                           pull=[0.06 if i == 0 else 0 for i in range(len(cat_agg))])
        th(fig9, legend=False); st.plotly_chart(fig9, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — MARGES
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "Marges":
    df = load_marges()

    with st.sidebar:
        st.markdown("**Filtres — Marges**")
        st.markdown("<div class='sidebar-label'>Période</div>", unsafe_allow_html=True)
        min_d = df["date_cmd"].min().date()
        max_d = df["date_cmd"].max().date()
        d_from = st.date_input("Du", value=min_d, min_value=min_d, max_value=max_d, key="m_from")
        d_to   = st.date_input("Au", value=max_d, min_value=min_d, max_value=max_d, key="m_to")
        if d_from > d_to:
            st.error("La date de début doit être avant la date de fin.")
            d_from, d_to = min_d, max_d
        st.markdown("<div class='sidebar-label'>Données</div>", unsafe_allow_html=True)
        produits = st.multiselect("Produit",   sorted(df["produit"].unique()),
                                  default=sorted(df["produit"].unique()), key="m_prod")
        cats     = st.multiselect("Catégorie", sorted(df["categorie_produit"].unique()),
                                  default=sorted(df["categorie_produit"].unique()), key="m_cats")
        wilayas  = st.multiselect("Wilaya",    sorted(df["wilaya"].unique()),
                                  default=sorted(df["wilaya"].unique()), key="m_wil")
        annees   = st.multiselect("Année",     sorted(df["annee"].unique()),
                                  default=sorted(df["annee"].unique()), key="m_yr")
        st.markdown("---")
        if st.button("Réinitialiser", use_container_width=True, key="m_reset"):
            st.rerun()

    mask = (
        (df["date_cmd"].dt.date >= d_from) & (df["date_cmd"].dt.date <= d_to) &
        df["produit"].isin(produits) & df["categorie_produit"].isin(cats) &
        df["wilaya"].isin(wilayas) & df["annee"].isin(annees)
    )
    dff = df[mask].copy()

    marge_tot  = dff["marge_totale"].sum()
    marge_moy  = dff["marge_unitaire"].mean()
    taux_marge = (marge_tot / dff["montant_ht"].sum() * 100) if dff["montant_ht"].sum() > 0 else 0
    ca_total   = dff["montant_ttc"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Marge Totale",        f"{marge_tot:,.0f} DA")
    k2.metric("Marge Unitaire Moy.", f"{marge_moy:,.0f} DA")
    k3.metric("Taux de Marge Moy.",  f"{taux_marge:.1f}%")
    k4.metric("CA Ventes TTC",       f"{ca_total:,.0f} DA")
    k5.metric("Lignes de Vente",     len(dff))
    st.markdown("<hr>", unsafe_allow_html=True)

    if dff.empty:
        st.warning("Aucune donnée pour les filtres sélectionnés.")
        st.stop()

    # 1
    st.markdown("## Marge par Produit")
    prod_agg = (dff.groupby("produit")
                .agg(marge_totale=("marge_totale","sum"), marge_unitaire=("marge_unitaire","mean"),
                     pu_vente=("pu_vente","mean"), pu_achat_moy=("pu_achat_moy","mean"),
                     qte=("qte","sum"), taux_marge_pct=("taux_marge_pct","mean"))
                .reset_index().sort_values("marge_totale", ascending=True))
    c1, c2 = st.columns(2, gap="large")
    with c1:
        fig1 = px.bar(prod_agg, x="marge_totale", y="produit", orientation="h",
                      color="marge_totale",
                      color_continuous_scale=[[0,"#fef3c7"],[0.4,"#10b981"],[1,"#065f46"]],
                      labels={"marge_totale":"Marge Totale (DA)","produit":""},
                      title="Marge totale par produit")
        fig1.update_coloraxes(showscale=False); th(fig1); st.plotly_chart(fig1, use_container_width=True)
    with c2:
        pu_melt = prod_agg.melt(id_vars="produit", value_vars=["pu_vente","pu_achat_moy"],
                                var_name="type", value_name="prix")
        pu_melt["type"] = pu_melt["type"].map({"pu_vente":"Prix de vente","pu_achat_moy":"Prix d'achat"})
        fig2 = px.bar(pu_melt, x="produit", y="prix", color="type", barmode="group",
                      color_discrete_sequence=[C[0], C[2]],
                      labels={"prix":"Prix Unitaire (DA)","produit":"","type":""},
                      title="Prix de vente vs Prix d'achat par produit")
        fig2.update_xaxes(tickangle=-20); th(fig2, legend=True); st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='card-title'>Détail par produit</div>", unsafe_allow_html=True)
    st.dataframe(
        prod_agg.sort_values("marge_totale", ascending=False)
        [["produit","pu_vente","pu_achat_moy","marge_unitaire","qte","marge_totale","taux_marge_pct"]]
        .rename(columns={"produit":"Produit","pu_vente":"PU Vente (DA)","pu_achat_moy":"PU Achat (DA)",
                         "marge_unitaire":"Marge Unitaire (DA)","qte":"Qté Vendue",
                         "marge_totale":"Marge Totale (DA)","taux_marge_pct":"Taux Marge (%)"}),
        use_container_width=True, hide_index=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 2
    st.markdown("## Marge par Catégorie")
    cat_agg = dff.groupby("categorie_produit")["marge_totale"].sum().reset_index().sort_values("marge_totale", ascending=True)
    c3, c4 = st.columns(2, gap="large")
    with c3:
        fig3 = px.bar(cat_agg, x="marge_totale", y="categorie_produit", orientation="h",
                      color="categorie_produit", color_discrete_sequence=C,
                      labels={"marge_totale":"Marge Totale (DA)","categorie_produit":""},
                      title="Marge totale par catégorie")
        th(fig3, legend=False); st.plotly_chart(fig3, use_container_width=True)
    with c4:
        fig4 = px.pie(cat_agg, values="marge_totale", names="categorie_produit", hole=0.55,
                      color_discrete_sequence=C, title="Répartition de la marge par catégorie")
        fig4.update_traces(textinfo="percent+label", textposition="outside",
                           pull=[0.05 if i == 0 else 0 for i in range(len(cat_agg))])
        th(fig4, legend=False); st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 3
    st.markdown("## Marge par Wilaya")
    c5, c6 = st.columns(2, gap="large")
    with c5:
        wil_agg = dff.groupby("wilaya")["marge_totale"].sum().reset_index().sort_values("marge_totale", ascending=True)
        fig5 = px.bar(wil_agg, x="marge_totale", y="wilaya", orientation="h",
                      color="wilaya", color_discrete_sequence=C,
                      labels={"marge_totale":"Marge Totale (DA)","wilaya":""},
                      title="Marge totale par wilaya")
        th(fig5, legend=False); st.plotly_chart(fig5, use_container_width=True)
    with c6:
        wil_cat = dff.groupby(["wilaya","categorie_produit"])["marge_totale"].sum().reset_index()
        fig6 = px.bar(wil_cat, x="wilaya", y="marge_totale", color="categorie_produit",
                      barmode="stack", color_discrete_sequence=C,
                      labels={"marge_totale":"Marge (DA)","wilaya":"","categorie_produit":"Catégorie"},
                      title="Marge par wilaya et catégorie")
        th(fig6, legend=True); st.plotly_chart(fig6, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 4
    st.markdown("## Evolution de la Marge dans le Temps")
    mois_cat = dff.groupby(["mois_ts","categorie_produit"])["marge_totale"].sum().reset_index().sort_values("mois_ts")
    fig7 = px.line(mois_cat, x="mois_ts", y="marge_totale", color="categorie_produit",
                   markers=True, color_discrete_sequence=C,
                   labels={"marge_totale":"Marge (DA)","mois_ts":"Mois","categorie_produit":"Catégorie"},
                   title="Evolution mensuelle de la marge par catégorie")
    fig7.update_traces(line_width=2, marker_size=7); th(fig7, legend=True); st.plotly_chart(fig7, use_container_width=True)

    c7, c8 = st.columns(2, gap="large")
    with c7:
        mois_prod = dff.groupby(["mois_ts","produit"])["marge_totale"].sum().reset_index().sort_values("mois_ts")
        fig8 = px.bar(mois_prod, x="mois_ts", y="marge_totale", color="produit", barmode="stack",
                      color_discrete_sequence=C,
                      labels={"marge_totale":"Marge (DA)","mois_ts":"Mois","produit":"Produit"},
                      title="Marge mensuelle par produit")
        th(fig8, legend=True); st.plotly_chart(fig8, use_container_width=True)
    with c8:
        yr_cat = dff.groupby(["annee","categorie_produit"])["marge_totale"].sum().reset_index()
        fig9 = px.bar(yr_cat, x="annee", y="marge_totale", color="categorie_produit", barmode="group",
                      color_discrete_sequence=C,
                      labels={"marge_totale":"Marge (DA)","annee":"Année","categorie_produit":"Catégorie"},
                      title="Marge par année et catégorie")
        th(fig9, legend=True); st.plotly_chart(fig9, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 5
    st.markdown("## Marge par Produit et Wilaya")
    prod_wil = dff.groupby(["produit","wilaya"])["marge_totale"].sum().reset_index()
    fig10 = px.bar(prod_wil, x="produit", y="marge_totale", color="wilaya", barmode="group",
                   color_discrete_sequence=C,
                   labels={"marge_totale":"Marge (DA)","produit":"","wilaya":"Wilaya"},
                   title="Marge par produit et wilaya")
    fig10.update_xaxes(tickangle=-20); th(fig10, legend=True); st.plotly_chart(fig10, use_container_width=True)

    pivot = (dff.groupby(["produit","wilaya"])["marge_totale"].sum().reset_index()
             .pivot(index="produit", columns="wilaya", values="marge_totale").fillna(0))
    fig11 = px.imshow(pivot, text_auto=True,
                      color_continuous_scale=[[0,"#f0fdf4"],[0.5,"#6ee7b7"],[1,"#065f46"]],
                      title="Heatmap marge (DA) — Produit x Wilaya", aspect="auto")
    fig11.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter", color="#374151", size=11),
                        margin=dict(l=8, r=8, t=40, b=8),
                        title_font=dict(size=13, color="#374151"))
    st.plotly_chart(fig11, use_container_width=True)
