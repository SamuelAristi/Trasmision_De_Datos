"""
Aplicación web Flask para gestión de limpieza de datos y visualización.
"""
import sys
import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import plotly.graph_objs as go
import plotly.utils

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.connection import db_connection
from src.services.order_service import OrderService
from src.utils.logger import logger

def convert_pandas_types(obj):
    """Convierte tipos de pandas/numpy a tipos nativos de Python para serialización JSON."""
    import numpy as np
    import pandas as pd
    
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif hasattr(obj, 'dtype'):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_pandas_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_pandas_types(item) for item in obj]
    else:
        return obj

app = Flask(__name__)
CORS(app)

# Inicializar servicios
order_service = OrderService()

@app.route('/')
def index():
    """Página principal del dashboard."""
    return render_template('index.html')

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """API endpoint para estadísticas del dashboard."""
    try:
        # Obtener estadísticas básicas
        total_query = "SELECT COUNT(*) as total FROM orders"
        total_orders = db_connection.execute_query(total_query)[0]['total']
        
        # Estadísticas por estado
        status_query = """
        SELECT status, COUNT(*) as count 
        FROM orders 
        GROUP BY status
        """
        status_stats = db_connection.execute_query(status_query)
        
        # Estadísticas por categoría
        category_query = """
        SELECT category, COUNT(*) as count, SUM(subtotal_amount) as total_amount
        FROM orders 
        GROUP BY category
        ORDER BY total_amount DESC
        """
        category_stats = db_connection.execute_query(category_query)
        
        # Estadísticas por año
        year_query = """
        SELECT EXTRACT(YEAR FROM order_date) as year, COUNT(*) as count, SUM(subtotal_amount) as total_amount
        FROM orders 
        GROUP BY EXTRACT(YEAR FROM order_date)
        ORDER BY year
        """
        year_stats = db_connection.execute_query(year_query)
        
        return jsonify({
            'total_orders': total_orders,
            'status_distribution': {item['status']: item['count'] for item in status_stats},
            'category_distribution': {item['category']: item['count'] for item in category_stats},
            'category_revenue': {item['category']: float(item['total_amount']) for item in category_stats},
            'yearly_stats': [
                {
                    'year': int(item['year']),
                    'orders': item['count'],
                    'revenue': float(item['total_amount'])
                } for item in year_stats
            ]
        })
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data-quality/report')
def data_quality_report():
    """API endpoint para reporte de calidad de datos."""
    try:
        report = order_service.get_data_quality_report()
        
        # Convertir tipos de datos no serializables
        report = convert_pandas_types(report)
        return jsonify(report)
    except Exception as e:
        logger.error(f"Error getting data quality report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data-cleaning/duplicates')
def check_duplicates():
    """API endpoint para verificar duplicados."""
    try:
        result = order_service.clean_duplicate_orders()
        response_data = {
            'total_records': int(result.total_records),
            'duplicates_found': int(result.cleaned_records),
            'warnings': int(result.warnings),
            'summary': result.cleaning_summary
        }
        # Convertir tipos de pandas/numpy
        response_data = convert_pandas_types(response_data)
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error checking duplicates: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data-cleaning/incomplete')
def check_incomplete():
    """API endpoint para verificar registros incompletos."""
    try:
        result = order_service.clean_incomplete_records()
        return jsonify({
            'total_records': result.total_records,
            'incomplete_records': result.cleaned_records,
            'errors': result.errors,
            'warnings': result.warnings,
            'summary': result.cleaning_summary
        })
    except Exception as e:
        logger.error(f"Error checking incomplete records: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data-cleaning/validate')
def validate_data():
    """API endpoint para validar tipos de datos."""
    try:
        result = order_service.validate_data_types()
        response_data = {
            'total_records': int(result.total_records),
            'errors': int(result.errors),
            'warnings': int(result.warnings),
            'summary': result.cleaning_summary
        }
        # Convertir tipos de pandas/numpy
        response_data = convert_pandas_types(response_data)
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error validating data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders')
def get_orders():
    """API endpoint para obtener órdenes con paginación."""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        status = request.args.get('status', '')
        category = request.args.get('category', '')
        
        # Construir query con filtros
        where_conditions = []
        params = {}
        
        if status:
            where_conditions.append("status = %(status)s")
            params['status'] = status
        
        if category:
            where_conditions.append("category = %(category)s")
            params['category'] = category
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        
        # Query para obtener total
        count_query = f"SELECT COUNT(*) as total FROM orders {where_clause}"
        total = db_connection.execute_query(count_query, params)[0]['total']
        
        # Query para obtener datos paginados
        offset = (page - 1) * per_page
        data_query = f"""
        SELECT * FROM orders 
        {where_clause}
        ORDER BY order_id DESC 
        LIMIT %(limit)s OFFSET %(offset)s
        """
        params.update({'limit': per_page, 'offset': offset})
        orders = db_connection.execute_query(data_query, params)
        
        return jsonify({
            'orders': orders,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/csv')
def export_csv():
    """API endpoint para exportar datos a CSV."""
    try:
        # Obtener todos los datos
        orders = order_service.get_all_orders()
        df = pd.DataFrame(orders)
        
        # Crear archivo CSV temporal
        filename = f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join('exports', filename)
        
        # Crear directorio si no existe
        os.makedirs('exports', exist_ok=True)
        
        # Guardar CSV
        df.to_csv(filepath, index=False)
        
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/powerbi/orders')
def powerbi_orders():
    """API endpoint específico para Power BI."""
    try:
        # Obtener datos optimizados para Power BI
        query = """
        SELECT 
            order_id,
            status,
            customer_name,
            order_date,
            quantity,
            subtotal_amount,
            tax_rate,
            shipping_cost,
            category,
            subcategory,
            EXTRACT(YEAR FROM order_date) as year,
            EXTRACT(MONTH FROM order_date) as month,
            EXTRACT(QUARTER FROM order_date) as quarter
        FROM orders 
        ORDER BY order_id DESC
        """
        orders = db_connection.execute_query(query)
        
        return jsonify({
            'data': orders,
            'last_updated': datetime.now().isoformat(),
            'total_records': len(orders)
        })
    except Exception as e:
        logger.error(f"Error getting Power BI data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/powerbi/summary')
def powerbi_summary():
    """API endpoint para resumen de datos para Power BI."""
    try:
        # Resumen por categoría
        category_summary = db_connection.execute_query("""
            SELECT 
                category,
                COUNT(*) as order_count,
                SUM(subtotal_amount) as total_revenue,
                AVG(subtotal_amount) as avg_order_value,
                SUM(quantity) as total_quantity
            FROM orders 
            GROUP BY category
            ORDER BY total_revenue DESC
        """)
        
        # Resumen por año
        yearly_summary = db_connection.execute_query("""
            SELECT 
                EXTRACT(YEAR FROM order_date) as year,
                COUNT(*) as order_count,
                SUM(subtotal_amount) as total_revenue,
                AVG(subtotal_amount) as avg_order_value
            FROM orders 
            GROUP BY EXTRACT(YEAR FROM order_date)
            ORDER BY year
        """)
        
        # Resumen por estado
        status_summary = db_connection.execute_query("""
            SELECT 
                status,
                COUNT(*) as order_count,
                SUM(subtotal_amount) as total_revenue
            FROM orders 
            GROUP BY status
            ORDER BY order_count DESC
        """)
        
        return jsonify({
            'category_summary': category_summary,
            'yearly_summary': yearly_summary,
            'status_summary': status_summary,
            'last_updated': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting Power BI summary: {e}")
        return jsonify({'error': str(e)}), 500

# ===== GESTIÓN DE ÓRDENES =====

@app.route('/api/orders/<int:order_id>')
def get_order(order_id):
    """API endpoint para obtener una orden específica."""
    try:
        query = "SELECT * FROM orders WHERE order_id = %(order_id)s"
        orders = db_connection.execute_query(query, {"order_id": order_id})
        
        if not orders:
            return jsonify({'error': 'Orden no encontrada'}), 404
        
        return jsonify(orders[0])
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """API endpoint para actualizar una orden existente."""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['status', 'customer_name', 'order_date', 'quantity', 
                          'subtotal_amount', 'tax_rate', 'shipping_cost', 'category', 'subcategory']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Construir query de actualización
        set_clauses = []
        params = {"order_id": order_id}
        
        for field in required_fields:
            set_clauses.append(f"{field} = %({field})s")
            params[field] = data[field]
        
        query = f"UPDATE orders SET {', '.join(set_clauses)} WHERE order_id = %(order_id)s"
        
        affected_rows = db_connection.execute_update(query, params)
        
        if affected_rows > 0:
            logger.info(f"Order {order_id} updated successfully")
            return jsonify({'message': 'Orden actualizada exitosamente', 'order_id': order_id})
        else:
            return jsonify({'error': 'Orden no encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Error updating order {order_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    """API endpoint para crear una nueva orden."""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['status', 'customer_name', 'order_date', 'quantity', 
                          'subtotal_amount', 'tax_rate', 'shipping_cost', 'category', 'subcategory']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo requerido: {field}'}), 400
        
        # Obtener el siguiente order_id
        max_id_query = "SELECT MAX(order_id) as max_id FROM orders"
        max_id_result = db_connection.execute_query(max_id_query)
        next_id = (max_id_result[0]['max_id'] or 0) + 1
        
        # Insertar nueva orden
        insert_query = """
        INSERT INTO orders (order_id, status, customer_name, order_date, quantity, 
                           subtotal_amount, tax_rate, shipping_cost, category, subcategory)
        VALUES (%(order_id)s, %(status)s, %(customer_name)s, %(order_date)s, %(quantity)s,
                %(subtotal_amount)s, %(tax_rate)s, %(shipping_cost)s, %(category)s, %(subcategory)s)
        """
        
        params = {
            'order_id': next_id,
            'status': data['status'],
            'customer_name': data['customer_name'],
            'order_date': data['order_date'],
            'quantity': data['quantity'],
            'subtotal_amount': data['subtotal_amount'],
            'tax_rate': data['tax_rate'],
            'shipping_cost': data['shipping_cost'],
            'category': data['category'],
            'subcategory': data['subcategory']
        }
        
        affected_rows = db_connection.execute_update(insert_query, params)
        
        if affected_rows > 0:
            logger.info(f"New order {next_id} created successfully")
            return jsonify({'message': 'Orden creada exitosamente', 'order_id': next_id}), 201
        else:
            return jsonify({'error': 'Error al crear la orden'}), 500
            
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """API endpoint para eliminar una orden."""
    try:
        # Verificar que la orden existe
        check_query = "SELECT order_id FROM orders WHERE order_id = %(order_id)s"
        existing = db_connection.execute_query(check_query, {"order_id": order_id})
        
        if not existing:
            return jsonify({'error': 'Orden no encontrada'}), 404
        
        # Eliminar la orden
        delete_query = "DELETE FROM orders WHERE order_id = %(order_id)s"
        affected_rows = db_connection.execute_update(delete_query, {"order_id": order_id})
        
        if affected_rows > 0:
            logger.info(f"Order {order_id} deleted successfully")
            return jsonify({'message': 'Orden eliminada exitosamente', 'order_id': order_id})
        else:
            return jsonify({'error': 'Error al eliminar la orden'}), 500
            
    except Exception as e:
        logger.error(f"Error deleting order {order_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>/status', methods=['PATCH'])
def update_order_status(order_id):
    """API endpoint para actualizar solo el estado de una orden."""
    try:
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'Campo status es requerido'}), 400
        
        # Verificar que la orden existe
        check_query = "SELECT order_id FROM orders WHERE order_id = %(order_id)s"
        existing = db_connection.execute_query(check_query, {"order_id": order_id})
        
        if not existing:
            return jsonify({'error': 'Orden no encontrada'}), 404
        
        # Actualizar solo el estado
        update_query = "UPDATE orders SET status = %(status)s WHERE order_id = %(order_id)s"
        affected_rows = db_connection.execute_update(update_query, {
            "order_id": order_id,
            "status": data['status']
        })
        
        if affected_rows > 0:
            logger.info(f"Order {order_id} status updated to {data['status']}")
            return jsonify({'message': 'Estado actualizado exitosamente', 'order_id': order_id, 'new_status': data['status']})
        else:
            return jsonify({'error': 'Error al actualizar el estado'}), 500
            
    except Exception as e:
        logger.error(f"Error updating order {order_id} status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/bulk-status', methods=['PATCH'])
def bulk_update_status():
    """API endpoint para actualizar el estado de múltiples órdenes."""
    try:
        data = request.get_json()
        
        if 'order_ids' not in data or 'status' not in data:
            return jsonify({'error': 'order_ids y status son requeridos'}), 400
        
        order_ids = data['order_ids']
        new_status = data['status']
        
        if not isinstance(order_ids, list) or len(order_ids) == 0:
            return jsonify({'error': 'order_ids debe ser una lista no vacía'}), 400
        
        # Construir query para múltiples IDs
        placeholders = ','.join(['%s'] * len(order_ids))
        update_query = f"UPDATE orders SET status = %s WHERE order_id IN ({placeholders})"
        
        params = [new_status] + order_ids
        affected_rows = db_connection.execute_update(update_query, params)
        
        logger.info(f"Bulk status update: {affected_rows} orders updated to {new_status}")
        return jsonify({
            'message': f'Estados actualizados exitosamente',
            'updated_count': affected_rows,
            'new_status': new_status
        })
        
    except Exception as e:
        logger.error(f"Error in bulk status update: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting web application...")
    app.run(debug=True, host='0.0.0.0', port=5000)
