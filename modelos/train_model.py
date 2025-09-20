import pandas as pd
import numpy as np
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os
import csv
import re

# =============================
# Configuración de rutas
# =============================
RUTA_EXCEL = r"C:\Users\Javier\Downloads\snic-departamentos-anual.xlsx"

DIR_PROVINCIA = r"C:\Web datos\modelos\saved_models\provincia"
DIR_PARTIDO = r"C:\Web datos\modelos\saved_models\partido"
DIR_DELITO = r"C:\Web datos\modelos\saved_models\delito"
DIR_DELITO_PROVINCIA = r"C:\Web datos\modelos\saved_models\delito_provincia"
DIR_DELITO_PARTIDO = r"C:\Web datos\modelos\saved_models\delito_partido"
OMITIDOS_PATH = r"C:\Web datos\modelos\modelos_omitidos.csv"
DATASET_LIMPIO = r"C:\Web datos\modelos\dataset_limpio.xlsx"

for d in [DIR_PROVINCIA, DIR_PARTIDO, DIR_DELITO, DIR_DELITO_PROVINCIA, DIR_DELITO_PARTIDO]:
    os.makedirs(d, exist_ok=True)

# =============================
# Función para limpiar nombres de archivo
# =============================
def sanitize_filename(name: str) -> str:
    """
    Limpia un string para que sea válido como nombre de archivo en Windows/Linux.
    Reemplaza caracteres no permitidos con '_'.
    """
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# =============================
# Función para registrar omisiones
# =============================
def registrar_omision(nombre_modelo, motivo):
    with open(OMITIDOS_PATH, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([nombre_modelo, motivo])

# =============================
# Función auxiliar para evaluar
# =============================
def evaluar_modelo(df, nombre):
    df = df[['ds', 'y']].dropna()
    if len(df) < 2:
        print(f"⚠️ {nombre} tiene menos de 2 datos válidos, se omite.")
        registrar_omision(nombre, "Menos de 2 datos válidos")
        return None, None

    n = len(df)
    train_size = int(n * 0.8)

    train = df.iloc[:train_size]
    test = df.iloc[train_size:]

    try:
        m = Prophet(yearly_seasonality=True)
        m.fit(train)

        future = m.make_future_dataframe(periods=len(test), freq="YE")
        forecast = m.predict(future)
        pred_test = forecast[['ds', 'yhat']].iloc[-len(test):]

        rmse = np.sqrt(mean_squared_error(test['y'], pred_test['yhat']))
        mae = mean_absolute_error(test['y'], pred_test['yhat'])
        mape = np.mean(np.abs((test['y'] - pred_test['yhat']) / test['y'])) * 100

        print(f"🔹 {nombre}")
        print(f"RMSE: {rmse:.2f} | MAE: {mae:.2f} | MAPE: {mape:.2f}%\n")

        return m, (rmse, mae, mape)

    except Exception as e:
        print(f"❌ Error entrenando {nombre}: {e}")
        registrar_omision(nombre, f"Error: {e}")
        return None, None

# =============================
# Función para crear y guardar modelos
# =============================
def crear_modelos(df, grupo_cols, dir_salida, prefijo):
    unique_combos = df[grupo_cols].drop_duplicates()
    for _, combo in unique_combos.iterrows():
        cond = np.logical_and.reduce([df[col] == combo[col] for col in grupo_cols])
        df_filtrado = df[cond].groupby('ds')['Cantidad'].sum().reset_index()
        df_filtrado = df_filtrado.rename(columns={'Cantidad': 'y'})

        nombre_modelo = f"{prefijo} - " + " / ".join([str(combo[c]) for c in grupo_cols])
        m, _ = evaluar_modelo(df_filtrado, nombre_modelo)

        if m:
            partes_nombre = []
            for col in grupo_cols:
                valor = str(combo[col]).replace(" ", "_")
                partes_nombre.append(f"{col}_{valor}")

            nombre_archivo = sanitize_filename("_".join(partes_nombre))
            ruta = os.path.join(dir_salida, f"{prefijo}_{nombre_archivo}.pkl")

            joblib.dump(m, ruta)
            print(f"✅ Modelo guardado en: {ruta}")

# =============================
# Cargar y limpiar dataset
# =============================
df = pd.read_excel(RUTA_EXCEL)

# Eliminar filas con 0 o NaN en "Cantidad"
filas_iniciales = len(df)
df = df.dropna(subset=['Año', 'Cantidad'])
df = df[df['Cantidad'] > 0]
filas_finales = len(df)

print(f"🧹 Filas eliminadas: {filas_iniciales - filas_finales}")
df.to_excel(DATASET_LIMPIO, index=False)
print(f"💾 Dataset limpio guardado en: {DATASET_LIMPIO}")

# Crear columna 'ds' a partir de "Año"
df['ds'] = pd.to_datetime(df['Año'], format='%Y')

# =============================
# Crear modelos
# =============================
crear_modelos(df, ['Provincia'], DIR_PROVINCIA, "Modelo Provincia")
crear_modelos(df, ['Partido'], DIR_PARTIDO, "Modelo Partido")
crear_modelos(df, ['Delito'], DIR_DELITO, "Modelo Delito")
crear_modelos(df, ['Delito', 'Provincia'], DIR_DELITO_PROVINCIA, "Modelo Delito-Provincia")
crear_modelos(df, ['Delito', 'Provincia', 'Partido'], DIR_DELITO_PARTIDO, "Modelo Delito-Provincia-Partido")
