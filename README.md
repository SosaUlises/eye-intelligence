# E&E Stock Intelligence

Sistema inteligente de análisis comercial desarrollado para E&E Calzados que integra información de ventas históricas, ventas recientes y stock actual para asistir la toma de decisiones mediante análisis de datos, Machine Learning e Inteligencia Artificial.

---

# Objetivo

El proyecto busca transformar los reportes exportados desde Dux Software en información útil para la gestión comercial.

A partir de los archivos Excel utilizados diariamente por la empresa, la aplicación:

- integra toda la información en un único dataset maestro;
- calcula indicadores comerciales;
- identifica patrones mediante Machine Learning;
- permite consultar los resultados utilizando lenguaje natural gracias a un LLM.

---

# Tecnologías utilizadas

## Backend

- Python 3
- Pandas
- NumPy
- Scikit-Learn

## Interfaz

- Streamlit

## Inteligencia Artificial

- Hugging Face Inference API
- Qwen 2.5 Instruct

---

# Arquitectura

```text
Reportes Excel (Dux)
        │
        ▼
Carga de archivos
        │
        ▼
Limpieza y normalización (Pandas)
        │
        ▼
Integración de datos
        │
        ▼
Dataset Maestro
        │
        ├─────────────► Dashboard Comercial
        │
        ├─────────────► Modelo K-Means
        │
        └─────────────► Asistente IA
```

---

# Datos utilizados

La aplicación trabaja con tres reportes exportados desde Dux Software.

## 1. Ventas mensuales por producto

Contiene el histórico mensual de ventas.

Período utilizado:

Julio 2025 → Julio 2026

---

## 2. Ventas detalladas

Detalle de operaciones recientes.

Período aproximado:

Últimos 60 días

---

## 3. Stock actual

Fotografía del stock disponible por depósito y sucursal al momento de la exportación.

---

# Flujo de procesamiento

## 1. Limpieza

Cada archivo es normalizado automáticamente.

Se corrigen:

- encabezados
- filas vacías
- columnas innecesarias
- tipos de datos

---

## 2. Integración

Los tres reportes son consolidados en un único Dataset Maestro.

El dataset contiene información como:

- stock disponible
- ventas históricas
- ventas recientes
- promedio mensual
- cobertura de stock
- rotación
- depósito
- marca
- rubro
- subrubro

---

## 3. Dashboard

Se generan indicadores comerciales interactivos como:

- stock disponible
- ventas históricas
- ventas recientes
- monto vendido
- productos sin movimiento
- productos más vendidos

Todos los indicadores pueden filtrarse por:

- depósito
- marca
- rubro

---

## 4. Machine Learning

Se construye un conjunto de variables comerciales y posteriormente se aplica un modelo K-Means para segmentar productos según su comportamiento.

Entre las variables utilizadas se encuentran:

- stock disponible
- ventas recientes mensualizadas
- promedio histórico mensual
- cobertura de stock
- índice de demanda
- rotación reciente

Los grupos obtenidos permiten identificar perfiles comerciales como:

- Alta rotación
- Cobertura elevada
- Rotación moderada
- Stock sin movimiento

---

## 5. Asistente IA

El asistente interpreta consultas en lenguaje natural.

Las búsquedas y filtros son resueltos previamente mediante Python y Pandas.

Posteriormente un LLM genera una explicación clara utilizando únicamente la información obtenida.

Ejemplos de consultas:

- ¿Qué productos tienen stock sin movimiento en Ricardone?
- Mostrame los 10 productos de mayor rotación.
- ¿Qué productos debería revisar primero?
- ¿Qué productos Athix presentan cobertura elevada?
- ¿Qué productos de Via Marte tienen mayor movimiento?

---

# Instalación

Clonar el repositorio.

```bash
git clone https://github.com/SosaUlises/eye-intelligence.git
```

Ingresar al proyecto.

```bash
cd eye-intelligence
```

Crear entorno virtual.

```bash
python -m venv .venv
```

Activarlo.

Windows

```bash
.venv\Scripts\activate
```

Instalar dependencias.

```bash
pip install -r requirements.txt
```

---

# Variables de entorno

Crear un archivo `.env`

```env
HF_TOKEN=token
HF_MODEL=Qwen/Qwen2.5-7B-Instruct
```

---

# Ejecutar

```bash
streamlit run app.py
```

---
# Versión online
https://eye-intelligence.streamlit.app

---
# Limitaciones

- El modelo K-Means realiza segmentación de productos; no predice ventas futuras.
- Las ventas recientes corresponden aproximadamente a los últimos 60 días.
- Los resultados dependen de la calidad de los datos exportados desde Dux Software.

---

# Autor

**Ulises Sosa**

Proyecto desarrollado para la materia **Python para Inteligencia Artificial** — Universidad Abierta Interamericana (UAI).
