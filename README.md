# Dashboard Estadísticas de Delitos – Flask + Bootstrap + Chart.js

## Descripción
Dashboard interactivo para el análisis y visualización de estadísticas de delitos en Argentina. Permite filtrar por provincia, partido, año y tipo de delito, mostrando KPIs, gráficos, rankings, comparativas y predicciones. Incluye opciones de exportación a CSV y PDF en todas las vistas principales.

## Tecnologías utilizadas
- Python 3.10+
- Flask
- Bootstrap 5
- Chart.js
- SQLite (base de datos)
- Prophet y scikit-learn (modelos predictivos)
- html2canvas y jsPDF (exportación PDF)

## Instalación
1. Clona el repositorio:
   ```bash
   git clone <URL del repo>
   ```
2. Instala los requerimientos de Python:
   ```bash
   pip install -r requirements.txt
   ```
3. (Opcional) Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```
4. Ejecuta la app:
   ```bash
   python app.py
   ```

## Estructura principal
```
app/
├── __init__.py
├── routes.py
├── models.py
├── services.py
├── static/
│   ├── css/
│   └── js/
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── rankings.html
│   ├── comparativa.html
│   ├── prediccion.html
│   └── tablero_regional.html
├── data/
│   └── delitos.db
├── requirements.txt
app.py
README.md
```

## Requerimientos Python
```
Flask
pandas
scikit-learn
prophet
joblib
plotly
```

## Requerimientos JS (CDN)
- Bootstrap 5
- Chart.js
- html2canvas
- jsPDF


## Modelos de Predicción y Entrenamiento

### Modelos utilizados
- **Prophet (serie temporal):** Utilizado para predecir la evolución de delitos a lo largo del tiempo, detectando tendencias y estacionalidades.
- **Regresión lineal (scikit-learn):** Empleado para estimar la variación de delitos en función de variables como provincia, partido y tipo de delito.

### Proceso de entrenamiento
1. **Obtención de datos:**
   - Se descargaron los datasets públicos del SNIC (Ministerio de Seguridad de Argentina) en formato CSV/XLSX.
   - Se consolidaron los archivos en una única base de datos SQLite (`app/data/delitos.db`).

2. **Limpieza y preprocesamiento:**
   - Se eliminaron filas con valores nulos o inconsistentes en campos clave (año, provincia, partido, delito, cantidad).
   - Se normalizaron nombres de provincias y partidos para evitar duplicados por errores de escritura.
   - Se filtraron registros con menos de 2 datos válidos para evitar sobreajuste y resultados irrelevantes.
   - Se agregaron columnas calculadas: tasas por población, variación interanual, género de víctimas.

3. **Entrenamiento de modelos:**
   - Prophet: Se entrenó un modelo por combinación relevante (provincia, partido, delito) usando la serie temporal de cantidad de delitos por año.
   - Regresión lineal: Se entrenó un modelo por combinación relevante, usando variables categóricas codificadas y cantidad de delitos como variable dependiente.
   - Los modelos se serializaron en formato `.pkl` o `.joblib` y se almacenaron en la carpeta `modelos/` (excluida por `.gitignore`).

4. **Validación y robustez:**
   - Se validó cada modelo con métricas de error (MAE, RMSE) y se descartaron aquellos con menos de 5 muestras o resultados inconsistentes.
   - Se documentaron los modelos omitidos en archivos de log para trazabilidad.

5. **Integración en el dashboard:**
   - Los modelos se cargan dinámicamente según los filtros seleccionados por el usuario.
   - El dashboard muestra la predicción, la variación estimada y una explicación automática del contexto y la robustez del modelo.

### Scripts de entrenamiento
- Los scripts de limpieza y entrenamiento se encuentran en la carpeta `scripts/` (no incluida en el repositorio por seguridad y tamaño).
- Ejemplo de flujo:
  ```python
  import pandas as pd
  from prophet import Prophet
  from sklearn.linear_model import LinearRegression
  # Cargar y limpiar datos
  df = pd.read_csv('delitos.csv')
  df = df.dropna(subset=['Año', 'Provincia', 'Partido', 'Delito', 'Cantidad'])
  # Entrenar Prophet
  modelo = Prophet()
  modelo.fit(df[['Año', 'Cantidad']].rename(columns={'Año':'ds','Cantidad':'y'}))
  # Entrenar regresión
  X = pd.get_dummies(df[['Provincia','Partido','Delito']])
  y = df['Cantidad']
  reg = LinearRegression().fit(X, y)
  ```

### Consideraciones
- Los modelos solo se muestran si hay datos suficientes y validados.
- La predicción es estimada y depende de la calidad y cantidad de datos históricos.
- Para nuevos entrenamientos, se recomienda actualizar los scripts y la base de datos siguiendo el mismo flujo.

## Funcionalidades principales
- Filtros inteligentes por provincia, partido, año y delito.
- KPIs dinámicos y visualizaciones interactivas.
- Rankings de delitos y variaciones.
- Comparativa VS entre provincias.
- Predicción de delitos con Prophet y regresión lineal.
- Exportación de tablas y gráficos a CSV y PDF.

## Despliegue
- Ejecuta `python app.py` y accede a `http://127.0.0.1:5000`.
- No requiere configuración adicional si usas la base de datos incluida.

## .gitignore sugerido
```
# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd

# Jupyter/Notebooks
.ipynb_checkpoints/

# Modelos y datos temporales
*.pkl
*.joblib
*.csv
*.xlsx
*.db
!app/data/delitos.db

# Archivos de entorno
.env

# Archivos de exportación
*.pdf
*.csv

# Archivos de sistema
.DS_Store
Thumbs.db
```

## Notas
- Los modelos predictivos y la base de datos se entrenan y actualizan desde scripts externos (no incluidos).
- Para producción, se recomienda usar un servidor WSGI como Gunicorn y configurar variables de entorno.
- El dashboard está optimizado para navegadores modernos y resoluciones desktop.

---

Desarrollado por Javier y GitHub Copilot.
