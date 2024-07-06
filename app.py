from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

# Diccionario para traducir nombres de columnas al español
COLUMN_TRANSLATIONS = {
    'fixed acidity': 'Acidez fija',
    'volatile acidity': 'Acidez volátil',
    'citric acid': 'Ácido cítrico',
    'residual sugar': 'Azúcar residual',
    'chlorides': 'Cloruros',
    'free sulfur dioxide': 'Dióxido de azufre libre',
    'total sulfur dioxide': 'Dióxido de azufre total',
    'density': 'Densidad',
    'pH': 'pH',
    'sulphates': 'Sulfatos',
    'alcohol': 'Alcohol',
    'quality': 'Calidad',
    'type': 'Tipo'
}

@app.route('/')
def index():
    # Define la ruta de los archivos CSV
    base_path = os.path.dirname(__file__)  # Obtiene el directorio del archivo app.py
    red_wine_path = os.path.join(base_path, 'winequality-red.csv')
    white_wine_path = os.path.join(base_path, 'winequality-white.csv')

    # Verifica que los archivos existen
    if not os.path.isfile(red_wine_path):
        raise FileNotFoundError(f"No se encuentra el archivo: {red_wine_path}")
    if not os.path.isfile(white_wine_path):
        raise FileNotFoundError(f"No se encuentra el archivo: {white_wine_path}")

    # Lee los archivos CSV
    red_wine = pd.read_csv(red_wine_path, delimiter=';')  # Ajusta el delimitador si es necesario
    white_wine = pd.read_csv(white_wine_path, delimiter=';')  # Ajusta el delimitador si es necesario

    # Añadir una columna 'type' para distinguir entre vino tinto y blanco
    red_wine['type'] = 'red'
    white_wine['type'] = 'white'

    # Combinar los DataFrames en uno solo
    combined_data = pd.concat([red_wine, white_wine])

    # Obtener parámetros de consulta
    sort_by = request.args.get('sort_by', 'fixed acidity')
    order_by = request.args.get('order_by', 'asc')
    page = int(request.args.get('page', 1))

    # Validar las columnas y el orden
    if sort_by not in combined_data.columns:
        sort_by = 'fixed acidity'
    if order_by not in ['asc', 'desc']:
        order_by = 'asc'

    # Ordenar los datos
    combined_data = combined_data.sort_values(by=sort_by, ascending=(order_by == 'asc'))

    # Paginación
    items_per_page = 15
    total_items = len(combined_data)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    paginated_data = combined_data[start_idx:end_idx]

    # Convertir el DataFrame a una lista de diccionarios
    data_list = paginated_data.to_dict(orient='records')

    # Convertir nombres de columnas a español para el menú de ordenación
    columns_in_spanish = {col: COLUMN_TRANSLATIONS.get(col, col) for col in combined_data.columns}

    return render_template(
        'index.html',
        data=data_list,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by,
        order_by=order_by,
        columns_in_spanish=columns_in_spanish
    )


@app.route('/graficos')
def graficos():
    # Lee los archivos CSV para obtener datos completos para los gráficos
    base_path = os.path.dirname(__file__)
    red_wine_path = os.path.join(base_path, 'winequality-red.csv')
    white_wine_path = os.path.join(base_path, 'winequality-white.csv')

    red_wine = pd.read_csv(red_wine_path, delimiter=';')
    white_wine = pd.read_csv(white_wine_path, delimiter=';')

    # Añadir una columna 'type' para distinguir entre vino tinto y blanco
    red_wine['type'] = 'red'
    white_wine['type'] = 'white'
    combined_data = pd.concat([red_wine, white_wine])

    # Verificar si las columnas necesarias están en el DataFrame
    if 'type' not in combined_data.columns:
        combined_data['type'] = 'unknown'

    # Datos para gráficos
    data_red_wine = red_wine[['fixed acidity', 'quality']].to_dict(orient='list')
    data_white_wine = white_wine[['fixed acidity', 'quality']].to_dict(orient='list')
    data_combined = combined_data[['fixed acidity', 'residual sugar', 'quality', 'type']].to_dict(orient='list')

    # Calcular datos para el mapa de calor
    correlation_matrix = combined_data[['fixed acidity', 'volatile acidity', 'citric acid', 'residual sugar', 
                                        'chlorides', 'free sulfur dioxide', 'total sulfur dioxide', 'density', 
                                        'pH', 'sulphates', 'alcohol', 'quality']].corr()
    heatmap_data = correlation_matrix.values.tolist()
    columns = correlation_matrix.columns.tolist()

    # Datos para el histograma de alcohol por tipo de vino
    alcohol_data_red = red_wine[['alcohol']].to_dict(orient='list')['alcohol']
    alcohol_data_white = white_wine[['alcohol']].to_dict(orient='list')['alcohol']

    return render_template(
        'graficos.html',
        data_red_wine=data_red_wine,
        data_white_wine=data_white_wine,
        data_combined=data_combined,
        heatmap_data=heatmap_data,
        columns=columns,
        alcohol_data_red=alcohol_data_red,
        alcohol_data_white=alcohol_data_white
    )

@app.route('/informacion')
def informacion():
    return render_template('informacion.html')

if __name__ == '__main__':
    app.run(debug=True)
