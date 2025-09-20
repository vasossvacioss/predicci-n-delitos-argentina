from . import app
from flask import render_template, jsonify, request
from .models import get_filtros
from .services import calcular_kpis, ranking_partidos
import pickle
from pathlib import Path
from flask import abort

@app.route('/acerca')
def acerca():
    return render_template('acerca.html')

@app.route('/api/ranking_delitos')
def api_ranking_delitos():
    from .models import get_top_delitos_agrupados
    filtros = {
        'provincia': request.args.get('provincia'),
        'partido': request.args.get('partido')
    }
    anio_inicio = int(request.args.get('anio_inicio', 2000))
    anio_fin = int(request.args.get('anio_fin', 2024))
    top_n = int(request.args.get('top', 5))
    result = get_top_delitos_agrupados(filtros, anio_inicio, anio_fin, top_n)
    return jsonify(result)

@app.route('/api/ranking_variacion')
def api_ranking_variacion():
    from .services import ranking_variacion
    filtros = {
        'provincia': request.args.get('provincia'),
        'delito': request.args.get('delito')
    }
    top_n = int(request.args.get('top', 5))
    result = ranking_variacion(filtros, top_n)
    return jsonify(result)

@app.route('/api/historico_financiero')
def api_historico_financiero():
    filtros = {
        'provincia': request.args.get('provincia'),
        'partido': request.args.get('partido'),
        'delito': request.args.get('delito')
    }
    from .models import get_tabla_historica_financiera
    tabla = get_tabla_historica_financiera(filtros)
    return jsonify(tabla)

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/rankings')
def rankings():
    return render_template('rankings.html')


@app.route('/tablero_regional')
def tablero_regional():
    return render_template('tablero_regional.html')

@app.route('/comparativa')
def comparativa():
    return render_template('comparativa.html')

@app.route('/prediccion')
def prediccion():
    return render_template('prediccion.html')

# API endpoints
@app.route('/api/filtros')
def api_filtros():
    return jsonify(get_filtros())

@app.route('/api/kpis')
def api_kpis():
    filtros = {
        'provincia': request.args.get('provincia'),
        'partido': request.args.get('partido'),
        'anio': request.args.get('anio'),
        'delito': request.args.get('delito')
    }
    return jsonify(calcular_kpis(filtros))

@app.route('/api/ranking_partidos')
def api_ranking_partidos():
    filtros = {
        'provincia': request.args.get('provincia'),
        'anio': request.args.get('anio'),
        'delito': request.args.get('delito')
    }
    top_n = int(request.args.get('top', 10))
    return jsonify(ranking_partidos(filtros, top_n))

@app.route('/api/predict')
def api_predict():
    import pickle, joblib
    from pathlib import Path
    import pandas as pd
    tipo = request.args.get('tipo')
    nivel = request.args.get('nivel')
    provincia = request.args.get('provincia')
    partido = request.args.get('partido')
    delito = request.args.get('delito')
    anio_inicio = int(request.args.get('anio_inicio', 2023))
    anio_fin = int(request.args.get('anio_fin', 2025))
    resultados = []
    delitos_agrupados = None
    # Determinar carpeta y nombre de archivo
    if tipo == 'prophet':
        base = Path('modelos/saved_models')
        if nivel == 'delito_partido' and provincia and partido and delito:
            nombre_archivo = f"Modelo Delito-Provincia-Partido_Delito_{delito.replace(' ','_')}_Provincia_{provincia.replace(' ','_')}_Partido_{partido.replace(' ','_')}.pkl"
            model_path = base / 'delito_partido' / nombre_archivo
        elif nivel == 'delito_provincia' and provincia and delito:
            nombre_archivo = f"Modelo Delito-Provincia_Delito_{delito.replace(' ','_')}_Provincia_{provincia.replace(' ','_')}.pkl"
            model_path = base / 'delito_provincia' / nombre_archivo
        elif nivel == 'delito' and delito:
            nombre_archivo = f"Modelo Delito_Delito_{delito.replace(' ','_')}.pkl"
            model_path = base / 'delito' / nombre_archivo
        elif nivel == 'partido' and partido:
            nombre_archivo = f"Modelo Partido_Partido_{partido.replace(' ','_')}.pkl"
            model_path = base / 'partido' / nombre_archivo
        elif nivel == 'provincia' and provincia:
            nombre_archivo = f"Modelo Provincia_Provincia_{provincia.replace(' ','_')}.pkl"
            model_path = base / 'provincia' / nombre_archivo
        else:
            return jsonify({'error':'Faltan parámetros'}), 400
        if not model_path.exists():
            return jsonify({'error':'Modelo no encontrado'}), 404
        import joblib
        try:
            model = joblib.load(model_path)
        except Exception:
            import pickle
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
        future = pd.DataFrame({'ds': pd.date_range(f'{anio_inicio}-01-01', f'{anio_fin}-01-01', freq='Y')})
        forecast = model.predict(future)
        for i, row in forecast.iterrows():
            resultados.append({'anio': row['ds'].year, 'valor': int(row['yhat'])})
        # Si nivel es provincia o partido, obtener delitos agrupados para gráfico circular
        if nivel in ['provincia', 'partido']:
            from .models import get_top_delitos_agrupados
            filtros = {}
            if provincia: filtros['provincia'] = provincia
            if partido: filtros['partido'] = partido
            delitos_agrupados = get_top_delitos_agrupados(filtros, anio_inicio, anio_fin, top_n=5)
    elif tipo == 'regresion':
        base = Path('modelos/saved_models_reg')
        if nivel == 'delito_partido' and provincia and partido and delito:
            nombre_modelo = f"modelo_Delito_{delito.replace(' ','_')}_Provincia_{provincia.replace(' ','_')}_Partido_{partido.replace(' ','_')}.pkl"
            nombre_scaler = f"scaler_Delito_{delito.replace(' ','_')}_Provincia_{provincia.replace(' ','_')}_Partido_{partido.replace(' ','_')}.pkl"
            model_path = base / 'delito_partido' / nombre_modelo
            scaler_path = base / 'delito_partido' / nombre_scaler
        elif nivel == 'delito_provincia' and provincia and delito:
            nombre_modelo = f"modelo_Delito_{delito.replace(' ','_')}_Provincia_{provincia.replace(' ','_')}.pkl"
            nombre_scaler = f"scaler_Delito_{delito.replace(' ','_')}_Provincia_{provincia.replace(' ','_')}.pkl"
            model_path = base / 'delito_provincia' / nombre_modelo
            scaler_path = base / 'delito_provincia' / nombre_scaler
        elif nivel == 'delito' and delito:
            nombre_modelo = f"modelo_Delito_{delito.replace(' ','_')}.pkl"
            nombre_scaler = f"scaler_Delito_{delito.replace(' ','_')}.pkl"
            model_path = base / 'delito' / nombre_modelo
            scaler_path = base / 'delito' / nombre_scaler
        elif nivel == 'partido' and partido:
            nombre_modelo = f"modelo_Partido_{partido.replace(' ','_')}.pkl"
            nombre_scaler = f"scaler_Partido_{partido.replace(' ','_')}.pkl"
            model_path = base / 'partido' / nombre_modelo
            scaler_path = base / 'partido' / nombre_scaler
        elif nivel == 'provincia' and provincia:
            nombre_modelo = f"modelo_Provincia_{provincia.replace(' ','_')}.pkl"
            nombre_scaler = f"scaler_Provincia_{provincia.replace(' ','_')}.pkl"
            model_path = base / 'provincia' / nombre_modelo
            scaler_path = base / 'provincia' / nombre_scaler
        else:
            return jsonify({'error':'Faltan parámetros'}), 400
        if not model_path.exists() or not scaler_path.exists():
            return jsonify({'error':'Modelo no encontrado'}), 404
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        for anio in range(anio_inicio, anio_fin+1):
            anio_num = anio - anio_inicio
            anio_cuadrado = anio_num ** 2
            X = pd.DataFrame({'año_num':[anio_num], 'año_cuadrado':[anio_cuadrado]})
            X_scaled = scaler.transform(X)
            valor = int(model.predict(X_scaled)[0])
            resultados.append({'anio': anio, 'valor': valor})
        # Si nivel es provincia o partido, obtener delitos agrupados para gráfico circular
        if nivel in ['provincia', 'partido']:
            from .models import get_top_delitos_agrupados
            filtros = {}
            if provincia: filtros['provincia'] = provincia
            if partido: filtros['partido'] = partido
            delitos_agrupados = get_top_delitos_agrupados(filtros, anio_inicio, anio_fin, top_n=5)
    else:
        return jsonify({'error':'Tipo de modelo inválido'}), 400
    response = {'resultados':resultados}
    if delitos_agrupados:
        response['delitos_agrupados'] = delitos_agrupados
    return jsonify(response)
