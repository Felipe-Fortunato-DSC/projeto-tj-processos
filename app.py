import base64
from datetime import datetime, date
from pathlib import Path

import pandas as pd
import streamlit as st

from database import (
    init_db,
    listar_usuarios,
    listar_usuarios_completo,
    get_tipo_usuario,
    verificar_senha,
    trocar_senha,
    adicionar_usuario,
    atualizar_usuario,
    redefinir_senha_usuario,
    remover_usuario,
    listar_opcoes,
    listar_parametros,
    adicionar_parametro,
    remover_parametro,
    inserir_processo,
    listar_processos,
    atualizar_processo,
    numero_processo_existe,
    db_mode,
)
from utils import calcular_dias_uteis, formatar_data_br, formatar_numero_processo, agora_br

# ─────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="TJRJ – Controle de Processos",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CSS PERSONALIZADO
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* Fundo geral */
.stApp {
    background-color: #f0f2f6;
}

/* Cabeçalho principal */
.header-container {
    padding: 8px 0;
    margin-bottom: 8px;
}
.header-title {
    color: #111111;
    font-size: 1.9rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: 0.5px;
}
.header-subtitle {
    color: #444444;
    font-size: 1.05rem;
    margin: 0;
}

/* Cards de métricas */
.metric-card {
    background: white;
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border-left: 4px solid #003580;
    text-align: center;
}

/* Botões primários */
.stButton > button[kind="primary"] {
    background-color: #003580;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.4rem 1.2rem;
}
.stButton > button[kind="primary"]:hover {
    background-color: #0052a3;
}

/* Formulário */
.form-section {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 16px;
}

/* Rodapé */
.footer {
    text-align: center;
    color: #888;
    font-size: 0.78rem;
    padding: 20px 0 8px 0;
    border-top: 1px solid #ddd;
    margin-top: 40px;
}
.footer a {
    color: #003580;
    text-decoration: none;
    font-weight: 600;
}

/* Login */
.login-box {
    background: white;
    border-radius: 16px;
    padding: 36px 40px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    max-width: 440px;
    margin: 60px auto 0 auto;
}
.login-title {
    color: #003580;
    font-size: 1.4rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 4px;
}
.login-sub {
    color: #888;
    font-size: 0.85rem;
    text-align: center;
    margin-bottom: 24px;
}

/* Tabela */
.dataframe thead tr th {
    background-color: #003580 !important;
    color: white !important;
}

/* Alertas de situação */
.badge-minutando  { color:#856404; background:#fff3cd; padding:2px 8px; border-radius:20px; font-size:0.8rem; }
.badge-juiza      { color:#0c5460; background:#d1ecf1; padding:2px 8px; border-radius:20px; font-size:0.8rem; }
.badge-corrigida  { color:#155724; background:#d4edda; padding:2px 8px; border-radius:20px; font-size:0.8rem; }
.badge-lancada    { color:#721c24; background:#f8d7da; padding:2px 8px; border-radius:20px; font-size:0.8rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES / OPÇÕES
# ─────────────────────────────────────────────
TIPOS_REU_PRESO = ["Não", "Sim"]
TIPOS_SISTEMA = ["DCP", "PJE"]

def get_tipos_processo():  return listar_opcoes("tipo_processo") or ["Sentença", "Embargos"]
def get_tipos_vara():      return listar_opcoes("vara")          or ["V JVD", "I JVD", "16 VC", "39 VC"]
def get_tipos_situacao():  return listar_opcoes("situacao")      or ["Minutando", "Juíza", "Corrigida", "Lançada"]
def get_tipos_responsavel(): return listar_usuarios()

LOGO_PATH = Path(__file__).parent / "assets" / "logo_tjrj.png"

def render_logo(width: int = 120, centered: bool = False):
    """Exibe o logo TJRJ. Usa arquivo local se existir, caso contrário exibe badge HTML."""
    if LOGO_PATH.exists():
        if centered:
            with open(str(LOGO_PATH), "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            st.markdown(
                f'<div style="display:flex;justify-content:center;margin-bottom:8px;">'
                f'<img src="data:image/png;base64,{img_b64}" width="{width}">'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.image(str(LOGO_PATH), width=width)
    else:
        align = "center" if centered else "left"
        size = f"{width}px"
        st.markdown(f"""
        <div style="text-align:{align}; margin-bottom:8px;">
            <div style="
                display:inline-flex; flex-direction:column;
                align-items:center; justify-content:center;
                width:{size}; height:{size};
                background:linear-gradient(135deg,#003580,#0052a3);
                border-radius:50%; border:4px solid #c8a951;
                box-shadow:0 4px 12px rgba(0,53,128,0.4);
            ">
                <span style="color:#c8a951;font-size:{int(width*0.18)}px;font-weight:900;letter-spacing:1px;">TJRJ</span>
                <span style="color:white;font-size:{int(width*0.09)}px;margin-top:2px;">⚖</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INICIALIZAR BANCO (uma vez por processo)
# ─────────────────────────────────────────────
@st.cache_resource
def _cached_init_db():
    init_db()

_cached_init_db()

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = ""
if "tipo_usuario" not in st.session_state:
    st.session_state.tipo_usuario = "Básico"
if "trocar_senha_modo" not in st.session_state:
    st.session_state.trocar_senha_modo = False
if "filtro_numero_ativo" not in st.session_state:
    st.session_state.filtro_numero_ativo = None
if "filtro_numero_ver" not in st.session_state:
    st.session_state.filtro_numero_ver = 0
if "processo_edit_ativo" not in st.session_state:
    st.session_state.processo_edit_ativo = None
if "processo_edit_ver" not in st.session_state:
    st.session_state.processo_edit_ver = 0


# ─────────────────────────────────────────────
# HELPER: cabeçalho com logo
# ─────────────────────────────────────────────
def render_header():
    render_logo(width=160, centered=False)
    st.markdown("""
    <div class="header-container">
        <p class="header-title">Tribunal de Justiça do Estado do Rio de Janeiro</p>
        <p class="header-subtitle">Sistema de Controle de Processos Judiciais</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")


def render_footer():
    st.markdown("""
    <div class="footer">
        Desenvolvido por <a href="#">Felipe Fortunato</a> &nbsp;|&nbsp; TJRJ – Controle de Processos &nbsp;|&nbsp; 2024
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# TELA DE LOGIN
# ─────────────────────────────────────────────
def tela_login():
    col_left, col_center, col_right = st.columns([1, 1.4, 1])
    with col_center:
        render_logo(width=220, centered=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center">
            <p style="color:#003580;font-size:1.3rem;font-weight:700;margin-bottom:2px">
                Sistema de Processos
            </p>
            <p style="color:#888;font-size:0.85rem;margin-bottom:24px">
                Tribunal de Justiça do Estado do Rio de Janeiro
            </p>
        </div>
        """, unsafe_allow_html=True)

        usuarios = listar_usuarios(incluir_master=True)

        with st.form("form_login", clear_on_submit=False):
            usuario_sel = st.selectbox("Usuário", usuarios, index=None, placeholder="Selecione o usuário...", key="sel_usuario")
            senha_input = st.text_input("Senha", type="password", key="inp_senha")
            btn_login = st.form_submit_button("Entrar", use_container_width=True, type="primary")

            if btn_login:
                if verificar_senha(usuario_sel, senha_input):
                    st.session_state.autenticado = True
                    st.session_state.usuario_logado = usuario_sel
                    st.session_state.tipo_usuario = get_tipo_usuario(usuario_sel)
                    st.session_state.trocar_senha_modo = False
                    st.rerun()
                else:
                    st.error("Senha incorreta. Tente novamente.")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Trocar Senha", use_container_width=True):
            st.session_state.trocar_senha_modo = True
            st.rerun()

    render_footer()


# ─────────────────────────────────────────────
# TELA TROCAR SENHA
# ─────────────────────────────────────────────
def tela_trocar_senha():
    col_left, col_center, col_right = st.columns([1, 1.4, 1])
    with col_center:
        render_logo(width=220, centered=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center">
            <p style="color:#003580;font-size:1.3rem;font-weight:700;margin-bottom:2px">Alterar Senha</p>
        </div>
        """, unsafe_allow_html=True)

        usuarios = listar_usuarios()

        with st.form("form_trocar_senha"):
            usuario_sel = st.selectbox("Usuário", usuarios)
            senha_atual = st.text_input("Senha Atual", type="password")
            nova_senha = st.text_input("Nova Senha", type="password")
            confirma = st.text_input("Confirmar Nova Senha", type="password")
            btn_alterar = st.form_submit_button("Alterar Senha", use_container_width=True, type="primary")

            if btn_alterar:
                if nova_senha != confirma:
                    st.error("As senhas não coincidem.")
                else:
                    ok, msg = trocar_senha(usuario_sel, senha_atual, nova_senha)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Voltar ao Login", use_container_width=True):
            st.session_state.trocar_senha_modo = False
            st.rerun()

    render_footer()


# ─────────────────────────────────────────────
# DIALOG: CONFIRMAR EDIÇÃO
# ─────────────────────────────────────────────
LABELS_CAMPOS = {
    "numero_processo": "Nº Processo",
    "data_conclusao":  "Data de Conclusão",
    "reu_preso":       "Réu Preso",
    "tipo":            "Tipo",
    "vara":            "Vara",
    "sistema":         "Sistema",
    "responsavel":     "Responsável",
    "situacao":        "Situação",
    "observacao":      "Observação",
}

@st.dialog("Confirmar Alterações")
def dialog_confirmar_edicao():
    pending  = st.session_state.get("pending_edicao", {})
    original = pending.get("original", {})
    novo     = pending.get("novo", {})

    alteracoes = [
        {"Campo": LABELS_CAMPOS[k], "De": str(original.get(k, "")), "Para": str(novo.get(k, ""))}
        for k in LABELS_CAMPOS
        if str(original.get(k, "")) != str(novo.get(k, ""))
    ]

    if not alteracoes:
        st.info("Nenhuma alteração detectada.")
    else:
        st.markdown("**Resumo das alterações:**")
        st.dataframe(pd.DataFrame(alteracoes), hide_index=True, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_conf, col_canc = st.columns(2)
    with col_conf:
        if st.button("Confirmar", type="primary", use_container_width=True, disabled=not alteracoes):
            d = pending["dados_salvar"]
            ok, msg = atualizar_processo(
                d["processo_id"], d["numero_processo"], d["reu_preso"],
                d["tipo"], d["vara"], d["sistema"], d["responsavel"],
                d["situacao"], d["observacao"], d["data_conclusao"], d["dias_aberto"],
            )
            st.session_state.pop("pending_edicao", None)
            if ok:
                st.session_state.processo_edit_ativo = None
                st.rerun()
            else:
                st.error(msg)
    with col_canc:
        if st.button("Cancelar", use_container_width=True):
            st.session_state.pop("pending_edicao", None)
            st.rerun()


# ─────────────────────────────────────────────
# ABA: VISUALIZAÇÃO / EDIÇÃO
# ─────────────────────────────────────────────
def aba_visualizacao():
    TIPOS_PROCESSO   = get_tipos_processo()
    TIPOS_VARA       = get_tipos_vara()
    TIPOS_SITUACAO   = get_tipos_situacao()
    TIPOS_RESPONSAVEL = get_tipos_responsavel()

    col_titulo_vis, col_btn_vis = st.columns([9, 1])
    col_titulo_vis.subheader("Processos Cadastrados")
    if col_btn_vis.button("🔄 Atualizar", key="btn_atualizar_vis", use_container_width=True):
        st.rerun()

    processos = listar_processos()

    if not processos:
        st.info("Nenhum processo cadastrado ainda.")
        return

    df = pd.DataFrame(processos)

    # Recalcular dias_aberto dinamicamente
    hoje = date.today()
    for idx, row in df.iterrows():
        try:
            dt = datetime.strptime(row["data_conclusao"][:10], "%Y-%m-%d").date()
            df.at[idx, "dias_aberto"] = calcular_dias_uteis(dt, hoje)
        except Exception:
            pass

    # Formatar datas para exibição
    df["data_conclusao_fmt"] = df["data_conclusao"].apply(formatar_data_br)
    df["criado_em_fmt"] = df["criado_em"].apply(formatar_data_br)
    df["numero_processo_fmt"] = df["numero_processo"].apply(formatar_numero_processo)

    # ── Filtros ──
    opcoes_numero = sorted([formatar_numero_processo(n) for n in df["numero_processo"].dropna().tolist()])

    # Badge do filtro de número ativo (acima do expander)
    if st.session_state.filtro_numero_ativo:
        badge_col, clear_col = st.columns([11, 1])
        badge_col.markdown(
            f'<div style="padding:4px 0">'
            f'<span style="background:#e8f0fe;color:#003580;padding:3px 12px;'
            f'border-radius:12px;font-size:0.82rem;font-weight:500;">'
            f'Nº Processo: <b>{st.session_state.filtro_numero_ativo}</b></span></div>',
            unsafe_allow_html=True,
        )
        if clear_col.button("✕ Limpar Filtro", key="clear_filtro_num"):
            st.session_state.filtro_numero_ativo = None
            st.rerun()

    with st.expander("Filtros", expanded=False):
        f1c1, f1c2, f1c3, f1c4 = st.columns(4)
        sel_numero = f1c1.selectbox(
            "Nº Processo",
            options=opcoes_numero,
            index=None,
            placeholder="Buscar processo...",
            key=f"filtro_num_{st.session_state.filtro_numero_ver}",
        )
        if sel_numero is not None:
            st.session_state.filtro_numero_ativo = sel_numero
            st.session_state.filtro_numero_ver += 1
            st.rerun()

        filtro_reu_preso   = f1c2.multiselect("Réu Preso", TIPOS_REU_PRESO)
        filtro_tipo        = f1c3.multiselect("Tipo", TIPOS_PROCESSO)
        filtro_responsavel = f1c4.multiselect("Responsável", TIPOS_RESPONSAVEL)

        f2c1, f2c2, f2c3, f2c4 = st.columns(4)
        filtro_vara     = f2c1.multiselect("Vara", TIPOS_VARA)
        filtro_sistema  = f2c2.multiselect("Sistema", TIPOS_SISTEMA)
        filtro_situacao = f2c3.multiselect("Situação", TIPOS_SITUACAO)

    df_filtrado = df.copy()
    if st.session_state.filtro_numero_ativo:
        _digitos_filtro = "".join(c for c in st.session_state.filtro_numero_ativo if c.isdigit())
        df_filtrado = df_filtrado[df_filtrado["numero_processo"] == _digitos_filtro]
    if filtro_reu_preso:
        df_filtrado = df_filtrado[df_filtrado["reu_preso"].isin(filtro_reu_preso)]
    if filtro_tipo:
        df_filtrado = df_filtrado[df_filtrado["tipo"].isin(filtro_tipo)]
    if filtro_responsavel:
        df_filtrado = df_filtrado[df_filtrado["responsavel"].isin(filtro_responsavel)]
    if filtro_vara:
        df_filtrado = df_filtrado[df_filtrado["vara"].isin(filtro_vara)]
    if filtro_sistema:
        df_filtrado = df_filtrado[df_filtrado["sistema"].isin(filtro_sistema)]
    if filtro_situacao:
        df_filtrado = df_filtrado[df_filtrado["situacao"].isin(filtro_situacao)]

    # ── Métricas rápidas ──
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total", len(df_filtrado))
    m2.metric("Minutando", len(df_filtrado[df_filtrado["situacao"] == "Minutando"]))
    m3.metric("Juíza", len(df_filtrado[df_filtrado["situacao"] == "Juíza"]))
    m4.metric("Corrigida", len(df_filtrado[df_filtrado["situacao"] == "Corrigida"]))
    m5.metric("Lançada", len(df_filtrado[df_filtrado["situacao"] == "Lançada"]))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabela de visualização ──
    df_filtrado = df_filtrado.sort_values("dias_aberto", ascending=False).reset_index(drop=True)

    cols_exibir = {
        "numero_processo_fmt": "Nº Processo",
        "data_conclusao_fmt": "Conclusão",
        "reu_preso": "Réu Preso",
        "tipo": "Tipo",
        "vara": "Vara",
        "sistema": "Sistema",
        "responsavel": "Responsável",
        "situacao": "Situação",
        "dias_aberto": "Dias Úteis",
        "observacao": "Observação",
    }

    df_display = df_filtrado[list(cols_exibir.keys())].rename(columns=cols_exibir)
    df_display["Dias Úteis"] = df_display["Dias Úteis"].apply(lambda x: int(x) if pd.notna(x) else 0)

    # ── Paginação ──
    ROWS_PER_PAGE = 10
    total = len(df_display)
    total_paginas = max(1, -(-total // ROWS_PER_PAGE))  # ceil division

    if "pagina_atual" not in st.session_state:
        st.session_state.pagina_atual = 1
    # Resetar página ao filtrar
    if st.session_state.pagina_atual > total_paginas:
        st.session_state.pagina_atual = 1

    inicio = (st.session_state.pagina_atual - 1) * ROWS_PER_PAGE
    fim = inicio + ROWS_PER_PAGE
    df_pagina = df_display.iloc[inicio:fim]

    st.dataframe(
        df_pagina,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Situação": st.column_config.SelectboxColumn(
                "Situação",
                options=TIPOS_SITUACAO,
            ),
            "Dias Úteis": st.column_config.NumberColumn("Dias Úteis", format="%d dias"),
        },
    )

    # Controles de navegação
    col_prev, col_info, col_next = st.columns([1, 3, 1])
    with col_prev:
        if st.button("← Anterior", disabled=st.session_state.pagina_atual <= 1, use_container_width=True):
            st.session_state.pagina_atual -= 1
            st.rerun()
    with col_info:
        st.markdown(
            f"<div style='text-align:center;padding-top:6px;color:#555;font-size:0.9rem;'>"
            f"Página {st.session_state.pagina_atual} de {total_paginas} &nbsp;|&nbsp; {total} processo(s)"
            f"</div>",
            unsafe_allow_html=True,
        )
    with col_next:
        if st.button("Próxima →", disabled=st.session_state.pagina_atual >= total_paginas, use_container_width=True):
            st.session_state.pagina_atual += 1
            st.rerun()

    # ── Seção de edição ──
    st.markdown("---")
    st.subheader("Editar Processo")

    numeros_raw = df_filtrado["numero_processo"].tolist()
    numeros = [formatar_numero_processo(n) for n in numeros_raw]
    if not numeros:
        st.info("Nenhum processo disponível para edição com os filtros atuais.")
        return

    # Garantir que o processo ativo ainda existe na lista atual
    if st.session_state.processo_edit_ativo not in numeros:
        st.session_state.processo_edit_ativo = None

    sel_editar = st.selectbox(
        "Selecione o processo para editar:",
        options=numeros,
        index=None,
        placeholder="Buscar processo...",
        key=f"sel_editar_{st.session_state.processo_edit_ver}",
    )
    if sel_editar is not None:
        st.session_state.processo_edit_ativo = sel_editar
        st.session_state.processo_edit_ver += 1
        st.rerun()

    if st.session_state.processo_edit_ativo is None:
        st.info("Selecione um processo acima para editar.")
        return

    processo_sel = st.session_state.processo_edit_ativo

    badge_col, clear_col = st.columns([11, 1])
    badge_col.markdown(
        f'<div style="padding:4px 0">'
        f'<span style="background:#e8f0fe;color:#003580;padding:3px 12px;'
        f'border-radius:12px;font-size:0.82rem;font-weight:500;">'
        f'Editando: <b>{processo_sel}</b></span></div>',
        unsafe_allow_html=True,
    )
    if clear_col.button("✕ Limpar Filtro", key="clear_edit_processo"):
        st.session_state.processo_edit_ativo = None
        st.rerun()
    _digitos_edit = "".join(c for c in processo_sel if c.isdigit())
    linha = df_filtrado[df_filtrado["numero_processo"] == _digitos_edit].iloc[0]

    with st.form("form_edicao"):
        try:
            dt_original = datetime.strptime(str(linha["data_conclusao"])[:16], "%Y-%m-%d %H:%M")
        except Exception:
            dt_original = agora_br()
        data_atual = dt_original.date()
        hora_original = dt_original.time()

        e1, e2 = st.columns(2)
        novo_numero = e1.text_input("Número do Processo", value=linha["numero_processo"])
        nova_data = e2.date_input("Data de Conclusão", value=data_atual)

        e3, e4 = st.columns(2)
        novo_reu_preso = e3.selectbox(
            "Réu Preso",
            TIPOS_REU_PRESO,
            index=TIPOS_REU_PRESO.index(linha["reu_preso"]) if linha["reu_preso"] in TIPOS_REU_PRESO else 0,
        )
        novo_tipo = e4.selectbox(
            "Tipo",
            TIPOS_PROCESSO,
            index=TIPOS_PROCESSO.index(linha["tipo"]) if linha["tipo"] in TIPOS_PROCESSO else 0,
        )

        e5, e6 = st.columns(2)
        nova_vara = e5.selectbox(
            "Vara",
            TIPOS_VARA,
            index=TIPOS_VARA.index(linha["vara"]) if linha["vara"] in TIPOS_VARA else 0,
        )
        novo_sistema = e6.selectbox(
            "Sistema",
            TIPOS_SISTEMA,
            index=TIPOS_SISTEMA.index(linha["sistema"]) if linha["sistema"] in TIPOS_SISTEMA else 0,
        )

        e7, e8 = st.columns(2)
        novo_responsavel = e7.selectbox(
            "Responsável",
            TIPOS_RESPONSAVEL,
            index=TIPOS_RESPONSAVEL.index(linha["responsavel"]) if linha["responsavel"] in TIPOS_RESPONSAVEL else 0,
        )
        nova_situacao = e8.selectbox(
            "Situação",
            TIPOS_SITUACAO,
            index=TIPOS_SITUACAO.index(linha["situacao"]) if linha["situacao"] in TIPOS_SITUACAO else 0,
        )

        nova_obs = st.text_area("Observação", value=linha["observacao"] or "", height=80)

        btn_salvar = st.form_submit_button("Salvar Alterações", type="primary", use_container_width=True)

        if btn_salvar:
            nova_data_conclusao = datetime.combine(nova_data, hora_original)
            dias = calcular_dias_uteis(nova_data, date.today())
            st.session_state.pending_edicao = {
                "original": {
                    "numero_processo": linha["numero_processo"],
                    "data_conclusao":  str(data_atual),
                    "reu_preso":       linha["reu_preso"],
                    "tipo":            linha["tipo"],
                    "vara":            linha["vara"],
                    "sistema":         linha["sistema"],
                    "responsavel":     linha["responsavel"],
                    "situacao":        linha["situacao"],
                    "observacao":      linha["observacao"] or "",
                },
                "novo": {
                    "numero_processo": novo_numero.strip(),
                    "data_conclusao":  str(nova_data),
                    "reu_preso":       novo_reu_preso,
                    "tipo":            novo_tipo,
                    "vara":            nova_vara,
                    "sistema":         novo_sistema,
                    "responsavel":     novo_responsavel,
                    "situacao":        nova_situacao,
                    "observacao":      nova_obs.strip(),
                },
                "dados_salvar": {
                    "processo_id":    int(linha["id"]),
                    "numero_processo": novo_numero.strip(),
                    "reu_preso":       novo_reu_preso,
                    "tipo":            novo_tipo,
                    "vara":            nova_vara,
                    "sistema":         novo_sistema,
                    "responsavel":     novo_responsavel,
                    "situacao":        nova_situacao,
                    "observacao":      nova_obs.strip(),
                    "data_conclusao":  nova_data_conclusao,
                    "dias_aberto":     dias,
                },
            }
            st.rerun()

    if st.session_state.get("pending_edicao"):
        dialog_confirmar_edicao()


# ─────────────────────────────────────────────
# DIALOG: NÚMERO DE PROCESSO DUPLICADO
# ─────────────────────────────────────────────
@st.dialog("Processo Já Cadastrado")
def dialog_processo_duplicado():
    numero = st.session_state.get("numero_duplicado", "")
    st.error(f"O número **{formatar_numero_processo(numero)}** já existe na base de dados.")
    st.markdown("Verifique o número informado ou consulte o processo já cadastrado na aba de visualização.")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Fechar", use_container_width=True):
        st.session_state.pop("numero_duplicado", None)
        st.session_state.pop("pending_inclusao", None)
        st.rerun()


# ─────────────────────────────────────────────
# DIALOG: NÚMERO DE PROCESSO FORA DO PADRÃO
# ─────────────────────────────────────────────
@st.dialog("Número de Processo Inválido")
def dialog_numero_invalido(qtd_digitos: int):
    st.error(
        f"Número do processo fora do padrão. "
        f"A Resolução 65/2008 exige exatamente 20 dígitos no formato "
        f"**NNNNNNN-DD.AAAA.J.TR.OOOO** "
        f"(detectados: {qtd_digitos} dígito{'s' if qtd_digitos != 1 else ''})."
    )
    st.markdown("""
| Segmento | Descrição |
|----------|-----------|
| NNNNNNN | Número sequencial do processo (7 dígitos) |
| DD | Dígito verificador (controle matemático) |
| AAAA | Ano de ajuizamento |
| J | Ramo do Judiciário (8 = Justiça Estadual) |
| TR | Código do tribunal |
| OOOO | Código da unidade de origem (vara/comarca) |
""")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Fechar", use_container_width=True):
        st.rerun()


# ─────────────────────────────────────────────
# DIALOG: CONFIRMAR INCLUSÃO SEM CONCLUSÃO
# ─────────────────────────────────────────────
@st.dialog("Atenção")
def dialog_confirmar_sem_conclusao():
    st.warning("Este processo **não** foi aberto para conclusão. Deseja continuar?")
    st.markdown("<br>", unsafe_allow_html=True)
    col_conf, col_canc = st.columns(2)
    with col_conf:
        if st.button("Sim, continuar", type="primary", use_container_width=True):
            dados = st.session_state.pop("pending_inclusao")
            ok, msg = inserir_processo(dados)
            if ok:
                st.session_state.inclusao_sucesso = msg
                st.rerun()
            else:
                st.session_state.numero_duplicado = dados["numero_processo"]
                st.rerun()
    with col_canc:
        if st.button("Cancelar", use_container_width=True):
            st.session_state.pop("pending_inclusao", None)
            st.rerun()


# ─────────────────────────────────────────────
# ABA: INCLUSÃO DE NOVO PROCESSO
# ─────────────────────────────────────────────
def aba_inclusao():
    TIPOS_PROCESSO    = get_tipos_processo()
    TIPOS_VARA        = get_tipos_vara()
    TIPOS_SITUACAO    = get_tipos_situacao()
    TIPOS_RESPONSAVEL = get_tipos_responsavel()

    st.subheader("Incluir Novo Processo")

    if "inclusao_sucesso" in st.session_state:
        st.success(st.session_state.pop("inclusao_sucesso"))


    agora = agora_br()

    with st.form("form_novo_processo", clear_on_submit=True):
        abrir_conclusao = st.checkbox("Conclusão Aberta")

        col1, col2 = st.columns(2)

        numero_processo = col1.text_input(
            "Número do Processo *",
            placeholder="Ex: 0001234-56.2024.8.19.0001",
            help="Digite o número completo do processo",
        )

        reu_preso = col2.selectbox("Réu Preso *", TIPOS_REU_PRESO)

        col3, col4 = st.columns(2)
        tipo = col3.selectbox("Tipo *", TIPOS_PROCESSO)
        vara = col4.selectbox("Vara *", TIPOS_VARA)

        col5, col6 = st.columns(2)
        sistema = col5.selectbox("Sistema *", TIPOS_SISTEMA)
        usuario_logado = st.session_state.usuario_logado
        idx_responsavel = TIPOS_RESPONSAVEL.index(usuario_logado) if usuario_logado in TIPOS_RESPONSAVEL else 0
        responsavel = col6.selectbox("Responsável *", TIPOS_RESPONSAVEL, index=idx_responsavel)

        situacao = st.selectbox("Situação *", TIPOS_SITUACAO)

        observacao = st.text_area("Observação", placeholder="Justificativa / observação livre...", height=100)

        st.markdown("---")
        btn_incluir = st.form_submit_button("Incluir Processo", type="primary", use_container_width=True)

        if btn_incluir:
            _digitos = "".join(c for c in numero_processo if c.isdigit())
            if not numero_processo.strip():
                st.error("O número do processo é obrigatório.")
            elif len(_digitos) != 20:
                st.session_state.numero_invalido_digitos = len(_digitos)
                st.rerun()
            elif numero_processo_existe(_digitos):
                st.session_state.numero_duplicado = numero_processo.strip()
                st.rerun()
            else:
                if abrir_conclusao:
                    data_conclusao_val = agora.strftime("%Y-%m-%d %H:%M:%S")
                    dias_aberto_val = calcular_dias_uteis(agora.date(), date.today())
                else:
                    data_conclusao_val = None
                    dias_aberto_val = None

                dados = {
                    "data_conclusao": data_conclusao_val,
                    "numero_processo": _digitos,
                    "reu_preso": reu_preso,
                    "tipo": tipo,
                    "vara": vara,
                    "sistema": sistema,
                    "responsavel": responsavel,
                    "situacao": situacao,
                    "dias_aberto": dias_aberto_val,
                    "observacao": observacao.strip(),
                    "criado_por": st.session_state.usuario_logado,
                }
                if abrir_conclusao:
                    ok, msg = inserir_processo(dados)
                    if ok:
                        st.session_state.inclusao_sucesso = msg
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.session_state.pending_inclusao = dados
                    st.rerun()

    if "numero_invalido_digitos" in st.session_state:
        qtd = st.session_state.pop("numero_invalido_digitos")
        dialog_numero_invalido(qtd)

    if "numero_duplicado" in st.session_state:
        dialog_processo_duplicado()

    if st.session_state.get("pending_inclusao"):
        dialog_confirmar_sem_conclusao()


# ─────────────────────────────────────────────
# ABA: GERENCIAMENTO (apenas administradores)
# ─────────────────────────────────────────────
@st.dialog("Confirmar Exclusão")
def dialog_confirmar_exclusao_usuario():
    uid   = st.session_state.get("excluir_usuario_id")
    nome  = st.session_state.get("excluir_usuario_nome", "")
    st.warning(f"Deseja realmente remover o usuário **{nome}**? Esta ação não pode ser desfeita.")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("Confirmar", type="primary", use_container_width=True):
        ok, msg = remover_usuario(uid, st.session_state.usuario_logado)
        st.session_state.pop("excluir_usuario_id",   None)
        st.session_state.pop("excluir_usuario_nome", None)
        if ok:
            st.rerun()
        else:
            st.error(msg)
    if c2.button("Cancelar", use_container_width=True):
        st.session_state.pop("excluir_usuario_id",   None)
        st.session_state.pop("excluir_usuario_nome", None)
        st.rerun()


@st.dialog("Confirmar Exclusão")
def dialog_confirmar_exclusao_parametro():
    pid   = st.session_state.get("excluir_param_id")
    valor = st.session_state.get("excluir_param_valor", "")
    st.warning(f"Deseja realmente remover o parâmetro **{valor}**? Esta ação não pode ser desfeita.")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("Confirmar", type="primary", use_container_width=True):
        ok, msg = remover_parametro(pid)
        st.session_state.pop("excluir_param_id",    None)
        st.session_state.pop("excluir_param_valor", None)
        if ok:
            st.rerun()
        else:
            st.error(msg)
    if c2.button("Cancelar", use_container_width=True):
        st.session_state.pop("excluir_param_id",    None)
        st.session_state.pop("excluir_param_valor", None)
        st.rerun()


@st.dialog("Novo Usuário")
def dialog_novo_usuario_ger():
    with st.form("form_add_user_ger"):
        nn = st.text_input("Nome *")
        ne = st.text_input("E-mail")
        nt = st.selectbox("Tipo *", ["Básico", "Administrador"])
        ns = st.text_input("Senha *", type="password")
        c1, c2 = st.columns(2)
        if c1.form_submit_button("Criar", type="primary", use_container_width=True):
            ok, msg = adicionar_usuario(nn, ne, nt, ns)
            if ok:
                st.session_state.pop("show_dialog_novo_usuario", None)
                st.rerun()
            else:
                st.error(msg)
        if c2.form_submit_button("Cancelar", use_container_width=True):
            st.session_state.pop("show_dialog_novo_usuario", None)
            st.rerun()


def aba_gerenciamento():
    col_titulo_ger, col_btn_ger = st.columns([9, 1])
    col_titulo_ger.subheader("Gerenciamento")
    if col_btn_ger.button("🔄 Atualizar", key="btn_atualizar_ger", use_container_width=True):
        st.rerun()

    sub_usuarios, sub_params = st.tabs(["Usuários", "Parâmetros"])

    # ── Usuários ──────────────────────────────
    with sub_usuarios:
        if "ger_user_page" not in st.session_state:
            st.session_state.ger_user_page = 1

        usuarios = listar_usuarios_completo()
        PAGE_SIZE = 10
        total = len(usuarios)
        total_pages = max(1, -(-total // PAGE_SIZE))
        if st.session_state.ger_user_page > total_pages:
            st.session_state.ger_user_page = 1

        start = (st.session_state.ger_user_page - 1) * PAGE_SIZE
        page_users = usuarios[start:start + PAGE_SIZE]

        # Inicializar session state apenas na primeira renderização de cada usuário (exceto Master)
        for u in page_users:
            if u["tipo_usuario"] == "Master":
                continue
            if f"ger_nome_{u['id']}"  not in st.session_state:
                st.session_state[f"ger_nome_{u['id']}"]  = u["nome"]
            if f"ger_email_{u['id']}" not in st.session_state:
                st.session_state[f"ger_email_{u['id']}"] = u["email"]
            if f"ger_tipo_{u['id']}"  not in st.session_state:
                st.session_state[f"ger_tipo_{u['id']}"]  = u["tipo_usuario"]

        # Cabeçalho da tabela
        h1, h2, h3, h4, h5 = st.columns([3, 3, 3, 2, 1])
        h1.markdown("**Nome**")
        h2.markdown("**E-mail**")
        h3.markdown("**Senha**")
        h4.markdown("**Tipo**")
        h5.markdown("**Ação**")
        st.divider()

        # Linhas editáveis
        for u in page_users:
            r1, r2, r3, r4, r5 = st.columns([3, 3, 3, 2, 1])
            if u["tipo_usuario"] == "Master":
                r1.text_input("", value=u["nome"], disabled=True, key=f"ger_nome_{u['id']}", label_visibility="collapsed")
                r2.text_input("", value="—", disabled=True, key=f"ger_email_{u['id']}", label_visibility="collapsed")
                r3.text_input("", value="••••••••", disabled=True, key=f"ger_senha_display_{u['id']}", label_visibility="collapsed")
                r4.selectbox("", ["Master"], disabled=True, key=f"ger_tipo_{u['id']}", label_visibility="collapsed")
                r5.button("🔒", key=f"ger_rm_{u['id']}", disabled=True)
            else:
                r1.text_input("", key=f"ger_nome_{u['id']}",  label_visibility="collapsed")
                r2.text_input("", key=f"ger_email_{u['id']}", label_visibility="collapsed")
                r3.text_input("", value="••••••••", disabled=True,
                              key=f"ger_senha_display_{u['id']}", label_visibility="collapsed")
                r4.selectbox("", ["Básico", "Administrador"],
                             key=f"ger_tipo_{u['id']}", label_visibility="collapsed")
                if r5.button("✕", key=f"ger_rm_{u['id']}", help=f"Remover {u['nome']}"):
                    st.session_state.excluir_usuario_id   = u["id"]
                    st.session_state.excluir_usuario_nome = u["nome"]
                    st.rerun()

        st.divider()

        # Linha de controles: salvar | paginação | novo
        bot_salvar, col_prev, col_info, col_next, col_add = st.columns([2, 1, 3, 1, 1])

        if bot_salvar.button("Salvar Alterações", type="primary", use_container_width=True):
            changed = 0
            for u in page_users:
                if u["tipo_usuario"] == "Master":
                    continue
                new_nome  = (st.session_state.get(f"ger_nome_{u['id']}",  u["nome"]) or "").strip()
                new_email = st.session_state.get(f"ger_email_{u['id']}", u["email"])
                new_tipo  = st.session_state.get(f"ger_tipo_{u['id']}",  u["tipo_usuario"])
                if not new_nome:
                    st.error(f"O nome do usuário não pode ser vazio.")
                    continue
                if new_nome != u["nome"] or new_email != u["email"] or new_tipo != u["tipo_usuario"]:
                    ok, msg = atualizar_usuario(u["id"], new_nome, new_email, new_tipo)
                    if not ok:
                        st.error(msg)
                    else:
                        changed += 1
            if changed:
                st.success(f"{changed} usuário(s) atualizado(s).")
                st.rerun()
            else:
                st.info("Nenhuma alteração detectada.")

        if col_prev.button("←", disabled=st.session_state.ger_user_page <= 1, use_container_width=True):
            st.session_state.ger_user_page -= 1
            st.rerun()

        col_info.markdown(
            f"<div style='text-align:center;padding-top:6px;color:#555;font-size:0.9rem;'>"
            f"Página {st.session_state.ger_user_page} de {total_pages} &nbsp;|&nbsp; {total} usuário(s)"
            f"</div>",
            unsafe_allow_html=True,
        )

        if col_next.button("→", disabled=st.session_state.ger_user_page >= total_pages, use_container_width=True):
            st.session_state.ger_user_page += 1
            st.rerun()

        if col_add.button("＋", use_container_width=True, help="Novo usuário"):
            st.session_state.show_dialog_novo_usuario = True
            st.rerun()

        if st.session_state.get("show_dialog_novo_usuario"):
            dialog_novo_usuario_ger()

        if st.session_state.get("excluir_usuario_id"):
            dialog_confirmar_exclusao_usuario()

    # ── Parâmetros ────────────────────────────
    with sub_params:
        st.markdown("#### Parâmetros das Colunas")

        categorias = {
            "tipo_processo": "Tipo de Processo",
            "vara":          "Vara",
            "situacao":      "Situação",
        }

        cols_params = st.columns(3)
        for col_widget, (categoria, label) in zip(cols_params, categorias.items()):
            with col_widget:
                st.markdown(f"##### {label}")
                params = listar_parametros(categoria)

                for p in params:
                    pc1, pc2 = st.columns([5, 1])
                    pc1.markdown(f"- {p['valor']}")
                    if pc2.button("✕", key=f"rm_{categoria}_{p['id']}", help=f"Remover {p['valor']}"):
                        st.session_state.excluir_param_id    = p["id"]
                        st.session_state.excluir_param_valor = p["valor"]
                        st.rerun()

                st.markdown("")
                with st.form(f"form_add_{categoria}"):
                    novo_val = st.text_input("Novo valor", key=f"inp_{categoria}")
                    if st.form_submit_button("Adicionar", use_container_width=True):
                        ok, msg = adicionar_parametro(categoria, novo_val)
                        if ok: st.rerun()
                        else:  st.error(msg)

        if st.session_state.get("excluir_param_id"):
            dialog_confirmar_exclusao_parametro()


# ─────────────────────────────────────────────
# APP PRINCIPAL (pós-login)
# ─────────────────────────────────────────────
def app_principal():
    render_header()

    # Barra lateral com info do usuário
    with st.sidebar:
        render_logo(width=160, centered=False)
        st.markdown(f"### Olá, **{st.session_state.usuario_logado}**")
        tipo_label = {"Master": "Master", "Administrador": "Administrador"}.get(st.session_state.tipo_usuario, "Básico")
        st.caption(f"Perfil: {tipo_label}")
        st.markdown(f"*{agora_br().strftime('%d/%m/%Y %H:%M')}*")
        if db_mode() == "motherduck":
            st.caption("🟢 MotherDuck")
        else:
            st.caption("🔴 Banco local (dados não persistem)")
        st.markdown("---")
        st.link_button("📖 Tutorial", url="https://github.com/Felipe-Fortunato-DSC/projeto-tj-processos/blob/main/TUTORIAL.md", use_container_width=True)
        st.markdown("---")
        if st.button("Sair", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.usuario_logado = ""
            st.session_state.tipo_usuario = "Básico"
            st.rerun()

    # Abas principais
    if st.session_state.tipo_usuario in ("Administrador", "Master"):
        tab_vis, tab_inc, tab_ger = st.tabs([
            "👁 Visualização de Processos", "➕ Incluir Novo Processo", "⚙ Gerenciamento"
        ])
        with tab_ger:
            aba_gerenciamento()
    else:
        tab_vis, tab_inc = st.tabs(["👁 Visualização de Processos", "➕ Incluir Novo Processo"])

    with tab_vis:
        aba_visualizacao()

    with tab_inc:
        aba_inclusao()

    render_footer()


# ─────────────────────────────────────────────
# ROTEAMENTO
# ─────────────────────────────────────────────
if not st.session_state.autenticado:
    if st.session_state.trocar_senha_modo:
        tela_trocar_senha()
    else:
        tela_login()
else:
    app_principal()
