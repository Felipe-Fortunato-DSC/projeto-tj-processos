# Tutorial do Sistema – TJRJ Controle de Processos

Este guia explica como usar o sistema de controle de processos judiciais do TJRJ.

---

## 1. Acesso ao Sistema

Na tela inicial, selecione seu **usuário** na lista e digite sua **senha**.

Clique em **Entrar**.

> Se for seu primeiro acesso, a senha padrão é `TJ12345`.  
> Recomendamos alterar a senha após o primeiro login (veja seção 2).

---

## 2. Trocar Senha

Na tela de login, clique em **Trocar Senha**.

Preencha:
- **Usuário**: selecione seu nome
- **Senha Atual**: sua senha atual
- **Nova Senha**: nova senha (mínimo 6 caracteres)
- **Confirmar Nova Senha**: repita a nova senha

Clique em **Alterar Senha**.

---

## 3. Navegação

Após o login, o sistema exibe abas no topo da página:

| Aba                  | Descrição                                          |
|----------------------|----------------------------------------------------|
| **Dashboard**        | Resumo geral com métricas dos processos            |
| **Processos**        | Listagem, busca e edição de processos              |
| **Novo Processo**    | Cadastro de novo processo                          |
| **Configurações**    | Gerenciamento de usuários e parâmetros *(somente Administrador/Master)* |

---

## 4. Dashboard

Exibe cartões com o resumo dos processos cadastrados:

- Total de processos
- Processos por situação (Minutando, Juíza, Corrigida, Lançada)
- Processos com réu preso

---

## 5. Cadastrar Novo Processo

Acesse a aba **Novo Processo** e preencha os campos:

| Campo              | Descrição                                                    |
|--------------------|--------------------------------------------------------------|
| **Nº Processo**    | Número no formato CNJ (20 dígitos). O sistema formata automaticamente. |
| **Data de Conclusão** | Data em que o processo foi concluso                       |
| **Réu Preso**      | Indica se o réu está preso (Sim / Não)                       |
| **Tipo**           | Tipo do processo (ex: Sentença, Embargos)                    |
| **Vara**           | Vara responsável pelo processo                               |
| **Sistema**        | Sistema de origem: DCP ou PJE                                |
| **Responsável**    | Usuário responsável pelo processo                            |
| **Situação**       | Situação atual: Minutando, Juíza, Corrigida ou Lançada       |
| **Observação**     | Campo livre para anotações                                   |

O campo **Dias Úteis** é calculado automaticamente com base na data de conclusão, descontando fins de semana e feriados nacionais e do estado do Rio de Janeiro.

Clique em **Cadastrar Processo** para salvar.

---

## 6. Listar e Buscar Processos

Na aba **Processos**, você verá todos os processos cadastrados.

**Filtros disponíveis:**
- Busca por número do processo
- Filtro por situação
- Filtro por responsável
- Filtro por vara
- Filtro por tipo

Os resultados são exibidos em tabela com as colunas principais. Clique em **Ver / Editar** em qualquer linha para abrir os detalhes.

---

## 7. Editar um Processo

Na listagem, clique no botão **Editar** ao lado do processo desejado.

Altere os campos necessários e clique em **Salvar Alterações**.

O sistema exibe um resumo das alterações realizadas antes de confirmar.

> Somente usuários com perfil **Administrador** ou **Master** podem editar processos.

---

## 8. Configurações (somente Administrador / Master)

### 8.1 Gerenciar Usuários

Acesse **Configurações > Usuários** para:

- **Adicionar** novo usuário (nome, e-mail, perfil e senha)
- **Editar** nome, e-mail e perfil de usuários existentes
- **Redefinir senha** de qualquer usuário
- **Remover** usuários (exceto o Master e o próprio usuário logado)

**Perfis disponíveis:**

| Perfil          | O que pode fazer                                          |
|-----------------|-----------------------------------------------------------|
| **Básico**      | Visualizar e cadastrar processos                          |
| **Administrador** | Tudo do Básico + editar processos, gerenciar usuários e parâmetros |
| **Master**      | Acesso total. Único no sistema, não pode ser removido.    |

### 8.2 Gerenciar Parâmetros

Acesse **Configurações > Parâmetros** para adicionar ou remover opções nas listas de:

- **Tipo de Processo** (ex: Sentença, Embargos)
- **Vara** (ex: V JVD, I JVD, 16 VC, 39 VC)
- **Situação** (ex: Minutando, Juíza, Corrigida, Lançada)

Para adicionar: digite o novo valor e clique em **Adicionar**.  
Para remover: clique no ícone de exclusão ao lado do item.

---

## 9. Indicadores de Situação

As situações dos processos são exibidas com cores para facilitar a leitura:

| Situação      | Cor                  |
|---------------|----------------------|
| Minutando     | Amarelo              |
| Juíza         | Azul claro           |
| Corrigida     | Verde                |
| Lançada       | Vermelho             |

---

## 10. Logout

Clique em **Sair** no canto superior da página para encerrar a sessão.

---

## Dúvidas ou Problemas

Entre em contato com o administrador do sistema.
