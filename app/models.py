def get_tabla_historica_financiera(filtros):
    conn = get_connection()
    cur = conn.cursor()
    query = 'SELECT "Año", Provincia, Partido, Delito, Cantidad FROM delitos WHERE 1=1'
    params = []
    if filtros.get('provincia'):
        query += ' AND Provincia = ?'
        params.append(filtros['provincia'])
    if filtros.get('partido'):
        query += ' AND Partido = ?'
        params.append(filtros['partido'])
    if filtros.get('delito'):
        query += ' AND Delito = ?'
        params.append(filtros['delito'])
    query += ' ORDER BY "Año" ASC'
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    # Agrupar por año y calcular totales según filtros
    historico = {}
    for row in rows:
        anio = row['Año']
        cantidad = int(row['Cantidad']) if row['Cantidad'] is not None else 0
        if anio not in historico:
            historico[anio] = {
                'Año': anio,
                'Provincia': row['Provincia'] if filtros.get('provincia') else 'Total país',
                'Partido': row['Partido'] if filtros.get('partido') else '-',
                'Delitos': {},
                'Total': 0
            }
        # Acumular por delito
        historico[anio]['Delitos'][row['Delito']] = historico[anio]['Delitos'].get(row['Delito'], 0) + cantidad
        # Acumular total según filtros
        if filtros.get('delito'):
            if row['Delito'] == filtros['delito']:
                historico[anio]['Total'] += cantidad
        elif filtros.get('partido'):
            historico[anio]['Total'] += cantidad
        elif filtros.get('provincia'):
            historico[anio]['Total'] += cantidad
        else:
            historico[anio]['Total'] += cantidad
    # Calcular delito más común y variación
    resultado = []
    prev_total = None
    for anio in sorted(historico.keys()):
        datos = historico[anio]
        delito_comun = '-'
        cantidad_delito_comun = 0
        if datos['Delitos']:
            delito_comun = max(datos['Delitos'], key=lambda k: datos['Delitos'][k])
            cantidad_delito_comun = datos['Delitos'][delito_comun]
        variacion = None
        if prev_total is not None and prev_total > 0:
            variacion = ((datos['Total'] - prev_total) / prev_total) * 100
        resultado.append({
            'Año': datos['Año'],
            'Provincia': datos['Provincia'],
            'Partido': datos['Partido'],
            'DelitoComun': f"{delito_comun} ({cantidad_delito_comun})" if delito_comun != '-' else '-',
            'Cantidad': datos['Total'],
            'Variacion': variacion
        })
        prev_total = datos['Total']
    return resultado
# Aquí van las funciones de consulta SQL
import sqlite3

DB_PATH = 'data/delitos.db'

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_filtros():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT Provincia FROM delitos WHERE Provincia != ""')
    provincias = [row['Provincia'] for row in cur.fetchall()]
    # Si hay parámetro provincia, filtrar partidos
    import flask
    provincia = flask.request.args.get('provincia')
    if provincia:
        cur.execute('SELECT DISTINCT Partido FROM delitos WHERE Partido != "" AND Provincia = ?', (provincia,))
    else:
        cur.execute('SELECT DISTINCT Partido FROM delitos WHERE Partido != ""')
    partidos = [row['Partido'] for row in cur.fetchall() if row['Partido'] != 'Departamento sin determinar']
    cur.execute('SELECT DISTINCT "Año" FROM delitos WHERE "Año" != ""')
    anios = [row['Año'] for row in cur.fetchall()]
    cur.execute('SELECT DISTINCT Delito FROM delitos WHERE Delito != ""')
    delitos = [row['Delito'] for row in cur.fetchall()]
    conn.close()
    return {
        'provincias': provincias,
        'partidos': partidos,
        'anios': anios,
        'delitos': delitos
    }

def get_data_filtrada(filtros):
    conn = get_connection()
    cur = conn.cursor()
    query = 'SELECT * FROM delitos WHERE 1=1'
    params = []
    if filtros.get('provincia'):
        query += ' AND Provincia = ?'
        params.append(filtros['provincia'])
    if filtros.get('partido'):
        query += ' AND Partido = ?'
        params.append(filtros['partido'])
    if filtros.get('anio'):
        query += ' AND "Año" = ?'
        params.append(filtros['anio'])
    if filtros.get('delito'):
        query += ' AND Delito = ?'
        params.append(filtros['delito'])
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_top_delitos_agrupados(filtros, anio_inicio, anio_fin, top_n=5):
    conn = get_connection()
    cur = conn.cursor()
    query = 'SELECT Delito, SUM(Cantidad) as total FROM delitos WHERE 1=1'
    params = []
    if filtros.get('provincia'):
        query += ' AND Provincia = ?'
        params.append(filtros['provincia'])
    if filtros.get('partido'):
        query += ' AND Partido = ?'
        params.append(filtros['partido'])
    query += ' AND "Año" >= ? AND "Año" <= ?'
    params.extend([anio_inicio, anio_fin])
    query += ' GROUP BY Delito ORDER BY total DESC'
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    delitos = [(row['Delito'], row['total']) for row in rows]
    top = delitos[:top_n]
    otros = delitos[top_n:]
    otros_total = sum([v for _, v in otros])
    result = [{'delito': d, 'valor': v} for d, v in top]
    if otros_total > 0:
        result.append({'delito': 'Otros delitos', 'valor': otros_total})
    return result
