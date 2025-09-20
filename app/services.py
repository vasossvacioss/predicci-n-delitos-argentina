# Ranking de variación interanual por provincia/partido
def ranking_variacion(filtros, top_n=5):
    datos = get_data_filtrada(filtros)
    variaciones = {}
    # Agrupar por provincia/partido y calcular variación porcentual entre años extremos
    for row in datos:
        clave = (row.get('Provincia'), row.get('Partido'))
        anio = int(row.get('Año')) if row.get('Año') else None
        cantidad = float(row.get('Cantidad', 0) or 0)
        if clave not in variaciones:
            variaciones[clave] = {}
        if anio:
            variaciones[clave][anio] = cantidad
    ranking = []
    for clave, anios in variaciones.items():
        if len(anios) >= 2:
            anios_ordenados = sorted(anios.items())
            inicial = anios_ordenados[0][1]
            final = anios_ordenados[-1][1]
            if inicial > 0:
                var_pct = ((final-inicial)/inicial)*100
                ranking.append({'provincia': clave[0], 'partido': clave[1], 'variacion': round(var_pct,2), 'inicial': inicial, 'final': final})
    # Top positivos y negativos
    ranking_pos = sorted([r for r in ranking if r['variacion'] > 0], key=lambda x: x['variacion'], reverse=True)[:top_n]
    ranking_neg = sorted([r for r in ranking if r['variacion'] < 0], key=lambda x: x['variacion'])[:top_n]
    return {'mayor_aumento': ranking_pos, 'mayor_descenso': ranking_neg}
from .models import get_data_filtrada

# Aquí va la lógica de KPIs, rankings y métricas

def calcular_kpis(filtros):
    datos = get_data_filtrada(filtros)
    total_delitos = sum(float(row.get('Cantidad', 0) or 0) for row in datos)
    total_victimas = sum(float(row.get('Cantidad Victimas', 0) or 0) for row in datos)
    total_masculinos = sum(float(row.get('Victimas Masculinos', 0) or 0) for row in datos)
    total_femeninas = sum(float(row.get('Victimas Femeninas', 0) or 0) for row in datos)
    promedio_delitos = round(total_delitos / len(datos), 2) if datos else 0
    delito_frecuente = None
    if datos:
        delitos_lista = [row.get('Delito') for row in datos if row.get('Delito')]
        if delitos_lista:
            delito_frecuente = max(set(delitos_lista), key=delitos_lista.count)
    anio_max = None
    if datos:
        anios_lista = [row.get('Año') for row in datos if row.get('Año')]
        if anios_lista:
            anio_max = max(set(anios_lista), key=anios_lista.count)
    porc_mujeres = round((total_femeninas / total_victimas) * 100, 1) if total_victimas else 0
    porc_hombres = round((total_masculinos / total_victimas) * 100, 1) if total_victimas else 0
    tasa_delitos = round(sum(float(row.get('Tasa de Hechos', 0) or 0) for row in datos) / len(datos), 2) if datos else 0
    tasa_victimas = round(sum(float(row.get('Tasa de Victimas', 0) or 0) for row in datos) / len(datos), 2) if datos else 0
    return {
        'total_delitos': total_delitos,
        'total_victimas': total_victimas,
        'anio_max': anio_max,
        'delito_frecuente': delito_frecuente,
        'promedio_delitos': promedio_delitos,
        'porc_mujeres': porc_mujeres,
        'porc_hombres': porc_hombres,
        'tasa_delitos': tasa_delitos,
        'tasa_victimas': tasa_victimas
    }

# Ejemplo de ranking por partido

def ranking_partidos(filtros, top_n=10):
    datos = get_data_filtrada(filtros)
    ranking = {}
    for row in datos:
        partido = row.get('Partido')
        if partido:
            ranking.setdefault(partido, 0)
            ranking[partido] += float(row.get('Cantidad', 0) or 0)
    top = sorted(ranking.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return top
