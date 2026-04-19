from datetime import datetime, timedelta, time
from core_config import CoreConfig

def to_time(hhmm):
    return datetime.strptime(hhmm, "%H:%M").time() if hhmm else None

def calcular_horas(entrada, almoco_saida, almoco_volta, saida):
    entrada = to_time(entrada)
    saida = to_time(saida)
    almoco_saida = to_time(almoco_saida)
    almoco_volta = to_time(almoco_volta)

    # Base references
    dt_hoje = datetime(2000, 1, 1) # Usamos uma data neutra
    dt_entrada = datetime.combine(dt_hoje, entrada)
    dt_saida = datetime.combine(dt_hoje, saida)
    
    # Se a saída for menor ou igual à entrada, passou da meia-noite
    if saida and entrada and dt_saida <= dt_entrada:
        dt_saida += timedelta(days=1)

    total_bruto = dt_saida - dt_entrada

    # Calcula intervalo
    intervalo = timedelta()
    if almoco_saida and almoco_volta:
        dt_almoco_saida = datetime.combine(dt_hoje, almoco_saida)
        dt_almoco_volta = datetime.combine(dt_hoje, almoco_volta)
        
        # Ajuste para caso o almoço passe da meia noite (incomum, mas possível para plantonistas)
        if dt_almoco_saida < dt_entrada:
            dt_almoco_saida += timedelta(days=1)
        if dt_almoco_volta <= dt_almoco_saida:
            dt_almoco_volta += timedelta(days=1)
            
        intervalo = dt_almoco_volta - dt_almoco_saida

    # Horas trabalhadas descontando intervalo
    trabalho_liquido = total_bruto - intervalo
    
    # Constante da Jornada (8h por exemplo)
    jornada = timedelta(hours=CoreConfig.JORNADA_DIARIA_HORAS)
    
    horas_normais = min(trabalho_liquido, jornada)
    horas_extras = max(trabalho_liquido - jornada, timedelta(0))

    # Cálculo do adicional noturno (22:00 até 05:00)
    # Precisamos iterar pelos minutos trabalhados (menos o intervalo) para cruzar a faixa noturna
    # Simplificação: verificar todos os minutos da entrada até a saída
    adicional_noturno_minutos = 0
    current_dt = dt_entrada
    
    # Calcula os bounds dos intervalos para não contar o almoço no adicional noturno
    is_in_break = False
    
    while current_dt < dt_saida:
        # Checa se está no horário de pausa
        if almoco_saida and almoco_volta:
            if dt_almoco_saida <= current_dt < dt_almoco_volta:
                current_dt += timedelta(minutes=1)
                continue
                
        # Checa se o horário atual é noturno (>= 22:00 ou < 05:00)
        h = current_dt.hour
        if h >= 22 or h < 5:
            adicional_noturno_minutos += 1
            
        current_dt += timedelta(minutes=1)

    adicional_noturno = timedelta(minutes=adicional_noturno_minutos)

    def to_decimal(td):
        return round(td.total_seconds() / 3600, 2)

    return {
        'horas_normais': to_decimal(horas_normais),
        'horas_extras': to_decimal(horas_extras),
        'adicional_noturno': to_decimal(adicional_noturno)
    }
