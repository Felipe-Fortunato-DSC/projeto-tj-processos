import bcrypt
import duckdb
import streamlit as st
from datetime import datetime
from utils import agora_br

SENHA_MASTER = "Master290915@"
DB_LOCAL = "data/tj_processos.db"


# ─────────────────────────────────────────────
# CONEXÃO (cached por sessão do Streamlit)
# ─────────────────────────────────────────────
@st.cache_resource
def get_conn() -> tuple[duckdb.DuckDBPyConnection, str]:
    try:
        token = st.secrets["motherduck"]["token"]
        tmp = duckdb.connect(f"md:?motherduck_token={token}")
        tmp.execute("CREATE DATABASE IF NOT EXISTS tj_processos")
        tmp.close()
        conn = duckdb.connect(f"md:tj_processos?motherduck_token={token}")
        return conn, "motherduck"
    except KeyError:
        conn = duckdb.connect(DB_LOCAL)
        return conn, "local"
    except Exception as e:
        st.error(f"Erro ao conectar ao MotherDuck: {e}")
        conn = duckdb.connect(DB_LOCAL)
        return conn, "local"


def _conn():
    conn, _ = get_conn()
    return conn


def db_mode() -> str:
    _, mode = get_conn()
    return mode


# ─────────────────────────────────────────────
# INICIALIZAÇÃO DAS TABELAS
# ─────────────────────────────────────────────
def init_db():
    conn = _conn()

    # ── Usuários ──
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id           INTEGER PRIMARY KEY,
            nome         VARCHAR UNIQUE NOT NULL,
            senha_hash   VARCHAR NOT NULL,
            email        VARCHAR DEFAULT '',
            tipo_usuario VARCHAR DEFAULT 'Administrador',
            criado_em    TIMESTAMP DEFAULT current_timestamp
        )
    """)
    conn.execute("CREATE SEQUENCE IF NOT EXISTS usuarios_id_seq START 1")

    # Migrações de colunas (tabela já existente)
    for col, definition in [
        ("email",        "VARCHAR DEFAULT ''"),
        ("tipo_usuario", "VARCHAR DEFAULT 'Administrador'"),
    ]:
        try:
            conn.execute(f"ALTER TABLE usuarios ADD COLUMN {col} {definition}")
        except Exception:
            pass

    # ── Processos ──
    conn.execute("""
        CREATE TABLE IF NOT EXISTS processos (
            id               INTEGER PRIMARY KEY,
            data_conclusao   TIMESTAMP,
            numero_processo  VARCHAR UNIQUE NOT NULL,
            reu_preso        VARCHAR NOT NULL,
            tipo             VARCHAR NOT NULL,
            vara             VARCHAR NOT NULL,
            sistema          VARCHAR NOT NULL,
            responsavel      VARCHAR NOT NULL,
            situacao         VARCHAR NOT NULL,
            dias_aberto      DOUBLE,
            observacao       VARCHAR DEFAULT '',
            criado_por       VARCHAR DEFAULT '',
            criado_em        TIMESTAMP DEFAULT current_timestamp,
            atualizado_em    TIMESTAMP
        )
    """)
    conn.execute("CREATE SEQUENCE IF NOT EXISTS processos_id_seq START 1")

    try:
        conn.execute("ALTER TABLE processos ALTER COLUMN data_conclusao DROP NOT NULL")
    except Exception:
        pass

    # Migração: coluna de data de alteração da situação
    try:
        conn.execute("ALTER TABLE processos ADD COLUMN data_alteracao_situacao TIMESTAMP")
        conn.execute(
            "UPDATE processos SET data_alteracao_situacao = criado_em "
            "WHERE data_alteracao_situacao IS NULL"
        )
    except Exception:
        pass

    # ── Parâmetros (Tipo, Vara, Situação) ──
    conn.execute("""
        CREATE TABLE IF NOT EXISTS parametros (
            id        INTEGER PRIMARY KEY,
            categoria VARCHAR NOT NULL,
            valor     VARCHAR NOT NULL,
            ordem     INTEGER DEFAULT 0
        )
    """)
    conn.execute("CREATE SEQUENCE IF NOT EXISTS parametros_id_seq START 1")

    # Criar usuário Master (único, imutável)
    master_existe = conn.execute(
        "SELECT COUNT(*) FROM usuarios WHERE tipo_usuario = 'Master'"
    ).fetchone()[0]
    if not master_existe:
        senha_hash = bcrypt.hashpw(SENHA_MASTER.encode(), bcrypt.gensalt()).decode()
        uid = conn.execute("SELECT nextval('usuarios_id_seq')").fetchone()[0]
        conn.execute(
            "INSERT INTO usuarios (id, nome, senha_hash, email, tipo_usuario) VALUES (?, ?, ?, ?, ?)",
            [uid, "Master", senha_hash, "", "Master"],
        )


# ─────────────────────────────────────────────
# PARÂMETROS (Tipo, Vara, Situação)
# ─────────────────────────────────────────────
def listar_opcoes(categoria: str) -> list[str]:
    conn = _conn()
    rows = conn.execute(
        "SELECT valor FROM parametros WHERE categoria = ? ORDER BY ordem, valor",
        [categoria],
    ).fetchall()
    return [r[0] for r in rows]


def listar_parametros(categoria: str) -> list[dict]:
    conn = _conn()
    rows = conn.execute(
        "SELECT id, valor FROM parametros WHERE categoria = ? ORDER BY ordem, valor",
        [categoria],
    ).fetchall()
    return [{"id": r[0], "valor": r[1]} for r in rows]


def adicionar_parametro(categoria: str, valor: str) -> tuple[bool, str]:
    conn = _conn()
    valor = valor.strip()
    if not valor:
        return False, "O valor não pode ser vazio."
    existe = conn.execute(
        "SELECT COUNT(*) FROM parametros WHERE categoria = ? AND valor = ?",
        [categoria, valor],
    ).fetchone()[0]
    if existe:
        return False, f"'{valor}' já existe nesta categoria."
    pid = conn.execute("SELECT nextval('parametros_id_seq')").fetchone()[0]
    ordem = conn.execute(
        "SELECT COALESCE(MAX(ordem), 0) + 1 FROM parametros WHERE categoria = ?", [categoria]
    ).fetchone()[0]
    conn.execute(
        "INSERT INTO parametros (id, categoria, valor, ordem) VALUES (?, ?, ?, ?)",
        [pid, categoria, valor, ordem],
    )
    conn.commit()
    return True, f"'{valor}' adicionado com sucesso."


def remover_parametro(param_id: int) -> tuple[bool, str]:
    conn = _conn()
    conn.execute("DELETE FROM parametros WHERE id = ?", [param_id])
    conn.commit()
    return True, "Parâmetro removido com sucesso."


# ─────────────────────────────────────────────
# USUÁRIOS
# ─────────────────────────────────────────────
def listar_usuarios(incluir_master: bool = False) -> list[str]:
    conn = _conn()
    if incluir_master:
        rows = conn.execute("SELECT nome FROM usuarios ORDER BY nome").fetchall()
    else:
        rows = conn.execute(
            "SELECT nome FROM usuarios WHERE tipo_usuario != 'Master' ORDER BY nome"
        ).fetchall()
    return [r[0] for r in rows]


def listar_usuarios_completo() -> list[dict]:
    conn = _conn()
    rows = conn.execute(
        "SELECT id, nome, email, tipo_usuario FROM usuarios ORDER BY nome"
    ).fetchall()
    def _norm(v):
        v = (v or "").strip().lower()
        if v == "master": return "Master"
        if v == "administrador": return "Administrador"
        return "Básico"
    return [{"id": r[0], "nome": r[1], "email": r[2] or "", "tipo_usuario": _norm(r[3])} for r in rows]


def get_tipo_usuario(nome: str) -> str:
    conn = _conn()
    row = conn.execute(
        "SELECT tipo_usuario FROM usuarios WHERE nome = ?", [nome]
    ).fetchone()
    if not row:
        return "Básico"
    val = (row[0] or "").strip().lower()
    if val == "master": return "Master"
    if val == "administrador": return "Administrador"
    return "Básico"


def verificar_senha(nome: str, senha: str) -> bool:
    conn = _conn()
    row = conn.execute(
        "SELECT senha_hash FROM usuarios WHERE nome = ?", [nome]
    ).fetchone()
    if not row:
        return False
    return bcrypt.checkpw(senha.encode(), row[0].encode())


def trocar_senha(nome: str, senha_atual: str, nova_senha: str) -> tuple[bool, str]:
    if not verificar_senha(nome, senha_atual):
        return False, "Senha atual incorreta."
    if len(nova_senha) < 6:
        return False, "A nova senha deve ter pelo menos 6 caracteres."
    nova_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
    conn = _conn()
    conn.execute(
        "UPDATE usuarios SET senha_hash = ? WHERE nome = ?", [nova_hash, nome]
    )
    conn.commit()
    return True, "Senha alterada com sucesso!"


def adicionar_usuario(nome: str, email: str, tipo_usuario: str, senha: str) -> tuple[bool, str]:
    nome = nome.strip()
    if not nome:
        return False, "O nome não pode ser vazio."
    if len(senha) < 6:
        return False, "A senha deve ter pelo menos 6 caracteres."
    conn = _conn()
    existe = conn.execute(
        "SELECT COUNT(*) FROM usuarios WHERE nome = ?", [nome]
    ).fetchone()[0]
    if existe:
        return False, f"Usuário '{nome}' já existe."
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    uid = conn.execute("SELECT nextval('usuarios_id_seq')").fetchone()[0]
    conn.execute(
        "INSERT INTO usuarios (id, nome, senha_hash, email, tipo_usuario) VALUES (?, ?, ?, ?, ?)",
        [uid, nome, senha_hash, email.strip(), tipo_usuario],
    )
    conn.commit()
    return True, f"Usuário '{nome}' criado com sucesso."


def atualizar_usuario(usuario_id: int, nome: str, email: str, tipo_usuario: str) -> tuple[bool, str]:
    nome = nome.strip()
    conn = _conn()
    row = conn.execute("SELECT tipo_usuario FROM usuarios WHERE id = ?", [usuario_id]).fetchone()
    if row and row[0] == "Master":
        return False, "O usuário Master não pode ser editado."
    conflito = conn.execute(
        "SELECT COUNT(*) FROM usuarios WHERE nome = ? AND id != ?", [nome, usuario_id]
    ).fetchone()[0]
    if conflito:
        return False, f"Nome '{nome}' já pertence a outro usuário."
    conn.execute(
        "UPDATE usuarios SET nome = ?, email = ?, tipo_usuario = ? WHERE id = ?",
        [nome, email.strip(), tipo_usuario, usuario_id],
    )
    conn.commit()
    return True, "Usuário atualizado com sucesso."


def redefinir_senha_usuario(usuario_id: int, nova_senha: str) -> tuple[bool, str]:
    if len(nova_senha) < 6:
        return False, "A senha deve ter pelo menos 6 caracteres."
    nova_hash = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
    conn = _conn()
    conn.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?", [nova_hash, usuario_id])
    conn.commit()
    return True, "Senha redefinida com sucesso."


def remover_usuario(usuario_id: int, nome_logado: str) -> tuple[bool, str]:
    conn = _conn()
    row = conn.execute("SELECT nome, tipo_usuario FROM usuarios WHERE id = ?", [usuario_id]).fetchone()
    if not row:
        return False, "Usuário não encontrado."
    nome, tipo = row
    if tipo == "Master":
        return False, "O usuário Master não pode ser removido."
    if nome == nome_logado:
        return False, "Você não pode remover sua própria conta."
    conn.execute("DELETE FROM usuarios WHERE id = ?", [usuario_id])
    conn.commit()
    return True, f"Usuário '{nome}' removido com sucesso."


# ─────────────────────────────────────────────
# PROCESSOS
# ─────────────────────────────────────────────
def numero_processo_existe(numero: str) -> bool:
    conn = _conn()
    digitos = "".join(c for c in numero if c.isdigit())
    return conn.execute(
        "SELECT COUNT(*) FROM processos "
        "WHERE regexp_replace(numero_processo, '[^0-9]', '', 'g') = ?",
        [digitos],
    ).fetchone()[0] > 0


def inserir_processo(dados: dict) -> tuple[bool, str]:
    conn = _conn()
    existe = conn.execute(
        "SELECT COUNT(*) FROM processos WHERE numero_processo = ?",
        [dados["numero_processo"]],
    ).fetchone()[0]
    if existe:
        return False, f"Número de processo '{dados['numero_processo']}' já cadastrado."

    pid = conn.execute("SELECT nextval('processos_id_seq')").fetchone()[0]
    agora = agora_br()
    conn.execute("""
        INSERT INTO processos (
            id, data_conclusao, numero_processo, reu_preso, tipo, vara,
            sistema, responsavel, situacao, dias_aberto, observacao,
            criado_por, atualizado_em, data_alteracao_situacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        pid,
        dados["data_conclusao"],
        dados["numero_processo"],
        dados["reu_preso"],
        dados["tipo"],
        dados["vara"],
        dados["sistema"],
        dados["responsavel"],
        dados["situacao"],
        dados["dias_aberto"],
        dados.get("observacao", ""),
        dados.get("criado_por", ""),
        agora,
        agora,
    ])
    conn.commit()
    return True, "Novo Processo Incluído com Sucesso!"


def listar_processos() -> list[dict]:
    conn = _conn()
    rows = conn.execute("""
        SELECT id, data_conclusao, numero_processo, reu_preso, tipo, vara,
               sistema, responsavel, situacao, dias_aberto, observacao,
               criado_por, criado_em, atualizado_em, data_alteracao_situacao
        FROM processos
        ORDER BY criado_em DESC
    """).fetchall()

    cols = [
        "id", "data_conclusao", "numero_processo", "reu_preso", "tipo",
        "vara", "sistema", "responsavel", "situacao", "dias_aberto",
        "observacao", "criado_por", "criado_em", "atualizado_em",
        "data_alteracao_situacao",
    ]
    return [dict(zip(cols, r)) for r in rows]


def atualizar_processo(
    processo_id: int,
    numero_processo: str,
    reu_preso: str,
    tipo: str,
    vara: str,
    sistema: str,
    responsavel: str,
    situacao: str,
    observacao: str,
    data_conclusao,
    dias_aberto: float,
) -> tuple[bool, str]:
    conn = _conn()
    conflito = conn.execute(
        "SELECT COUNT(*) FROM processos WHERE numero_processo = ? AND id != ?",
        [numero_processo, processo_id],
    ).fetchone()[0]
    if conflito:
        return False, f"Número de processo '{numero_processo}' já pertence a outro registro."

    row_atual = conn.execute(
        "SELECT situacao FROM processos WHERE id = ?", [processo_id]
    ).fetchone()
    situacao_mudou = row_atual and row_atual[0] != situacao
    agora = agora_br()

    if situacao_mudou:
        conn.execute("""
            UPDATE processos
            SET numero_processo = ?, reu_preso = ?, tipo = ?, vara = ?, sistema = ?,
                responsavel = ?, situacao = ?, observacao = ?,
                data_conclusao = ?, dias_aberto = ?, atualizado_em = ?,
                data_alteracao_situacao = ?
            WHERE id = ?
        """, [
            numero_processo, reu_preso, tipo, vara, sistema,
            responsavel, situacao, observacao,
            data_conclusao, dias_aberto, agora,
            agora,
            processo_id,
        ])
    else:
        conn.execute("""
            UPDATE processos
            SET numero_processo = ?, reu_preso = ?, tipo = ?, vara = ?, sistema = ?,
                responsavel = ?, situacao = ?, observacao = ?,
                data_conclusao = ?, dias_aberto = ?, atualizado_em = ?
            WHERE id = ?
        """, [
            numero_processo, reu_preso, tipo, vara, sistema,
            responsavel, situacao, observacao,
            data_conclusao, dias_aberto, agora,
            processo_id,
        ])
    conn.commit()
    return True, "Processo atualizado com sucesso!"
