from datetime import date, datetime, timedelta
import holidays


def calcular_dias_uteis(data_inicio: date, data_fim: date = None) -> float:
    """
    Calcula a quantidade de dias úteis entre data_inicio e data_fim (padrão: hoje),
    excluindo finais de semana e feriados do Brasil / Rio de Janeiro.
    """
    if data_fim is None:
        data_fim = date.today()

    if data_inicio > data_fim:
        return 0.0

    anos = set(range(data_inicio.year, data_fim.year + 1))
    feriados = set()
    for ano in anos:
        # Feriados nacionais
        feriados.update(holidays.Brazil(years=ano).keys())
        # Feriados estaduais do Rio de Janeiro
        feriados.update(holidays.Brazil(state="RJ", years=ano).keys())

    dias_uteis = 0
    atual = data_inicio
    while atual <= data_fim:
        if atual.weekday() < 5 and atual not in feriados:  # 0=seg ... 4=sex
            dias_uteis += 1
        atual += timedelta(days=1)

    return float(dias_uteis)


def formatar_numero_processo(numero: str) -> str:
    """Formata número de processo conforme Resolução CNJ 65/2008: NNNNNNN-DD.AAAA.J.TR.OOOO"""
    if not numero:
        return numero or ""
    digitos = "".join(c for c in str(numero) if c.isdigit())
    if len(digitos) == 20:
        return (
            f"{digitos[0:7]}-{digitos[7:9]}."
            f"{digitos[9:13]}.{digitos[13]}."
            f"{digitos[14:16]}.{digitos[16:20]}"
        )
    return numero


def formatar_data_br(dt_str: str) -> str:
    """Converte 'YYYY-MM-DD HH:MM:SS' para 'DD/MM/YYYY HH:MM'"""
    try:
        dt = datetime.strptime(dt_str[:16], "%Y-%m-%d %H:%M")
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return dt_str or ""
