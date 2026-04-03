# TJRJ – Controle de Processos Judiciais

Sistema web para controle e acompanhamento de processos judiciais, desenvolvido com Streamlit e banco de dados DuckDB (local ou nuvem via MotherDuck).

## Funcionalidades

- **Login com autenticação segura** via bcrypt
- **Cadastro e edição de processos** judiciais com validação de número (CNJ 65/2008)
- **Cálculo automático de dias úteis** descontando finais de semana e feriados nacionais e estaduais (RJ)
- **Filtros e busca** na listagem de processos
- **Gerenciamento de usuários** com três níveis de perfil: Master, Administrador e Básico
- **Parâmetros configuráveis** (tipos de processo, varas, situações)
- **Suporte a dois ambientes de banco**: local (DuckDB/SQLite) e nuvem (MotherDuck)

## Estrutura do Projeto

```
projeto-tj-processos/
├── app.py              # Interface Streamlit (telas e lógica de navegação)
├── database.py         # Acesso ao banco de dados (DuckDB), modelos e queries
├── utils.py            # Funções utilitárias (dias úteis, formatação)
├── requirements.txt    # Dependências Python
├── assets/
│   └── logo_tjrj.png   # Logo do TJRJ
├── data/
│   └── .gitkeep        # Pasta onde o banco local é gerado (data/tj_processos.db)
└── .streamlit/
    ├── config.toml     # Tema e configurações do Streamlit
    └── secrets.toml    # Token MotherDuck (NÃO versionar — já no .gitignore)
```

## Pré-requisitos

- Python 3.10+
- pip

## Instalação

```bash
# Clone o repositório
git clone https://github.com/Felipe-Fortunato-DSC/projeto-tj-processos.git
cd projeto-tj-processos

# Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Instale as dependências
pip install -r requirements.txt
```

## Execução Local

```bash
streamlit run app.py
```

O banco de dados é criado automaticamente em `data/tj_processos.db` na primeira execução.

## Configuração de Banco na Nuvem (MotherDuck)

Para usar o MotherDuck em vez do banco local, crie o arquivo `.streamlit/secrets.toml` com o seu token:

```toml
[motherduck]
token = "seu_token_aqui"
```

> Este arquivo está no `.gitignore` e nunca deve ser versionado.

No Streamlit Cloud, adicione o token pelo painel **Settings > Secrets** da aplicação.

## Perfis de Usuário

| Perfil         | Permissões                                                        |
|----------------|-------------------------------------------------------------------|
| **Master**     | Acesso total. Único, criado automaticamente. Não pode ser removido. |
| **Administrador** | Cadastra e edita processos, gerencia usuários e parâmetros.   |
| **Básico**     | Visualiza e cadastra processos. Não acessa configurações.         |

## Usuários Padrão

Na primeira execução, os seguintes usuários são criados automaticamente:

| Usuário     | Perfil         | Senha Padrão |
|-------------|----------------|--------------|
| Master      | Master         | `Master290915@` |
| Monique     | Administrador  | `TJ12345`    |
| Alice       | Básico         | `TJ12345`    |
| Maria Clara | Básico         | `TJ12345`    |
| Larissa     | Básico         | `TJ12345`    |

> Recomenda-se alterar as senhas padrão no primeiro acesso.

## Dependências

| Pacote      | Versão mínima | Uso                                      |
|-------------|---------------|------------------------------------------|
| streamlit   | 1.32.0        | Interface web                            |
| duckdb      | 0.10.0        | Banco de dados (local e MotherDuck)      |
| bcrypt      | 4.0.0         | Hash de senhas                           |
| pandas      | 2.0.0         | Manipulação de dados na interface        |
| holidays    | 0.46          | Feriados BR/RJ para cálculo de dias úteis |

## Deploy no Streamlit Cloud

1. Faça fork ou push do repositório para o GitHub
2. Acesse [streamlit.io/cloud](https://streamlit.io/cloud) e conecte o repositório
3. Defina o arquivo principal como `app.py`
4. Adicione o token MotherDuck em **Settings > Secrets**:
   ```toml
   [motherduck]
   token = "seu_token_aqui"
   ```

## Desenvolvido por

Felipe Fortunato — TJRJ, 2024
