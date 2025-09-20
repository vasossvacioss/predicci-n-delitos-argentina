import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
import csv
import re

# =============================
# Configuración de rutas
# =============================
RUTA_EXCEL = r"C:\Users\Javier\Downloads\snic-departamentos-anual.xlsx"

# Nuevas carpetas para modelos de regresión
DIR_PROVINCIA_REG = r"C:\Web datos\modelos\saved_models_reg\provincia"
DIR_PARTIDO_REG = r"C:\Web datos\modelos\saved_models_reg\partido"
DIR_DELITO_REG = r"C:\Web datos\modelos\saved_models_reg\delito"
DIR_DELITO_PROVINCIA_REG = r"C:\Web datos\modelos\saved_models_reg\delito_provincia"
DIR_DELITO_PARTIDO_REG = r"C:\Web datos\modelos\saved_models_reg\delito_partido"
OMITIDOS_PATH_REG = r"C:\Web datos\modelos\modelos_omitidos_reg.csv"
DATASET_LIMPIO_REG = r"C:\Web datos\modelos\dataset_limpio_reg.xlsx"

# Crear directorios
for d in [DIR_PROVINCIA_REG, DIR_PARTIDO_REG, DIR_DELITO_REG, 
          DIR_DELITO_PROVINCIA_REG, DIR_DELITO_PARTIDO_REG]:
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
def registrar_omision(nombre_modelo, motivo, archivo=OMITIDOS_PATH_REG):
    with open(archivo, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([nombre_modelo, motivo])

# =============================
# Función auxiliar para evaluar modelo de regresión
# =============================
def evaluar_modelo_regresion(X, y, nombre):
    if len(X) < 5:  # Mínimo de muestras para regresión
        print(f"⚠️ {nombre} tiene menos de 5 muestras, se omite.")
        registrar_omision(nombre, "Menos de 5 muestras")
        return None, None, None

    # Dividir en train y test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Escalar features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    try:
        # Entrenar modelo
        model = LinearRegression()
        model.fit(X_train_scaled, y_train)
        
        # Predecir
        y_pred = model.predict(X_test_scaled)
        
        # Calcular métricas
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"🔹 {nombre}")
        print(f"RMSE: {rmse:.2f} | MAE: {mae:.2f} | R²: {r2:.4f}")
        print(f"Coeficientes: {model.coef_} | Intercept: {model.intercept_:.2f}\n")
        
        return model, scaler, (rmse, mae, r2)
        
    except Exception as e:
        print(f"❌ Error entrenando {nombre}: {e}")
        registrar_omision(nombre, f"Error: {e}")
        return None, None, None

# =============================
# Función para crear y guardar modelos de regresión
# =============================
def crear_modelos_regresion(df, grupo_cols, dir_salida, prefijo):
    unique_combos = df[grupo_cols].drop_duplicates()
    
    for _, combo in unique_combos.iterrows():
        cond = np.logical_and.reduce([df[col] == combo[col] for col in grupo_cols])
        df_filtrado = df[cond].copy()
        
        # Crear features temporales
        df_filtrado['año_num'] = df_filtrado['Año'] - df_filtrado['Año'].min()
        df_filtrado['año_cuadrado'] = df_filtrado['año_num'] ** 2
        
        # Preparar datos para regresión
        X = df_filtrado[['año_num', 'año_cuadrado']]
        y = df_filtrado['Cantidad']
        
        nombre_modelo = f"{prefijo} - " + " / ".join([str(combo[c]) for c in grupo_cols])
        model, scaler, metrics = evaluar_modelo_regresion(X, y, nombre_modelo)
        
        if model:
            # Crear nombre del archivo
            partes_nombre = []
            for col in grupo_cols:
                valor = str(combo[col]).replace(" ", "_")
                partes_nombre.append(f"{col}_{valor}")
            
            nombre_archivo = sanitize_filename("_".join(partes_nombre))
            
            # Guardar modelo y scaler
            modelo_path = os.path.join(dir_salida, f"modelo_{nombre_archivo}.pkl")
            scaler_path = os.path.join(dir_salida, f"scaler_{nombre_archivo}.pkl")
            
            joblib.dump(model, modelo_path)
            joblib.dump(scaler, scaler_path)
            
            print(f"✅ Modelo guardado en: {modelo_path}")
            print(f"✅ Scaler guardado en: {scaler_path}")

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
df.to_excel(DATASET_LIMPIO_REG, index=False)
print(f"💾 Dataset limpio guardado en: {DATASET_LIMPIO_REG}")

# =============================
# Crear modelos de regresión
# =============================
print("🚀 Creando modelos de regresión lineal...")
crear_modelos_regresion(df, ['Provincia'], DIR_PROVINCIA_REG, "Regresión Provincia")
crear_modelos_regresion(df, ['Partido'], DIR_PARTIDO_REG, "Regresión Partido")
crear_modelos_regresion(df, ['Delito'], DIR_DELITO_REG, "Regresión Delito")
crear_modelos_regresion(df, ['Delito', 'Provincia'], DIR_DELITO_PROVINCIA_REG, "Regresión Delito-Provincia")
crear_modelos_regresion(df, ['Delito', 'Provincia', 'Partido'], DIR_DELITO_PARTIDO_REG, "Regresión Delito-Provincia-Partido")

print("🎯 Todos los modelos de regresión lineal han sido procesados!")