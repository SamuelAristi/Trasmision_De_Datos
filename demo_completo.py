"""
Demo completo del proyecto de limpieza de datos.
Este script demuestra todas las funcionalidades del proyecto.
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.connection import db_connection
from src.services.order_service import OrderService
from src.utils.logger import logger


def demo_completo():
    """Demo completo de todas las funcionalidades del proyecto."""
    print("🚀" + "=" * 60)
    print("   DEMO COMPLETO - PROYECTO DE LIMPIEZA DE DATOS")
    print("=" * 62)
    
    try:
        # 1. Verificar conexión
        print("\n1️⃣ VERIFICANDO CONEXIÓN A LA BASE DE DATOS")
        print("-" * 50)
        if db_connection.test_connection():
            print("✅ Conexión exitosa a PostgreSQL")
            print("✅ Base de datos: DropshipingDB")
            print("✅ Tabla: orders")
        else:
            print("❌ Error en la conexión")
            return
        
        # 2. Estadísticas básicas
        print("\n2️⃣ ESTADÍSTICAS BÁSICAS")
        print("-" * 50)
        total_query = "SELECT COUNT(*) as total FROM orders"
        total = db_connection.execute_query(total_query)[0]['total']
        print(f"📊 Total de órdenes: {total:,}")
        
        # 3. Inicializar servicio
        print("\n3️⃣ INICIALIZANDO SERVICIO DE LIMPIEZA")
        print("-" * 50)
        service = OrderService()
        print("✅ OrderService inicializado correctamente")
        
        # 4. Reporte de calidad
        print("\n4️⃣ REPORTE DE CALIDAD DE DATOS")
        print("-" * 50)
        report = service.get_data_quality_report()
        print(f"📈 Completitud promedio: {sum(report['data_completeness'].values()) / len(report['data_completeness']):.1f}%")
        print(f"📈 Duplicados detectados: {report['duplicate_records']}")
        
        # 5. Análisis de duplicados
        print("\n5️⃣ ANÁLISIS DE DUPLICADOS")
        print("-" * 50)
        dup_result = service.clean_duplicate_orders()
        if dup_result.cleaned_records > 0:
            print(f"⚠️  Duplicados encontrados: {dup_result.cleaned_records}")
            print("📋 Ejemplos de duplicados:")
            for example in dup_result.cleaning_summary.get('duplicate_examples', [])[:3]:
                print(f"   - ID: {example['order_id']}, Cliente: {example['customer_name']}")
        else:
            print("✅ No se encontraron duplicados")
        
        # 6. Análisis de registros incompletos
        print("\n6️⃣ ANÁLISIS DE REGISTROS INCOMPLETOS")
        print("-" * 50)
        inc_result = service.clean_incomplete_records()
        if inc_result.cleaned_records > 0:
            print(f"⚠️  Registros problemáticos: {inc_result.cleaned_records}")
            print(f"❌ Errores: {inc_result.errors}")
            print(f"⚠️  Warnings: {inc_result.warnings}")
        else:
            print("✅ No se encontraron registros incompletos")
        
        # 7. Validación de tipos de datos
        print("\n7️⃣ VALIDACIÓN DE TIPOS DE DATOS")
        print("-" * 50)
        val_result = service.validate_data_types()
        print(f"❌ Errores de tipo: {val_result.errors}")
        print(f"⚠️  Warnings de validación: {val_result.warnings}")
        
        # 8. Consultas específicas
        print("\n8️⃣ CONSULTAS ESPECÍFICAS")
        print("-" * 50)
        
        # Top categorías
        category_query = """
        SELECT category, COUNT(*) as count, SUM(subtotal_amount) as total
        FROM orders 
        GROUP BY category 
        ORDER BY total DESC
        """
        categories = db_connection.execute_query(category_query)
        print("🏆 Top categorías por ventas:")
        for i, cat in enumerate(categories, 1):
            print(f"   {i}. {cat['category']}: ${cat['total']:,.0f} ({cat['count']} órdenes)")
        
        # 9. Análisis temporal
        print("\n9️⃣ ANÁLISIS TEMPORAL")
        print("-" * 50)
        year_query = """
        SELECT EXTRACT(YEAR FROM order_date) as year, COUNT(*) as orders, SUM(subtotal_amount) as total
        FROM orders 
        GROUP BY EXTRACT(YEAR FROM order_date)
        ORDER BY year
        """
        years = db_connection.execute_query(year_query)
        print("📅 Órdenes por año:")
        for year_data in years:
            print(f"   {int(year_data['year'])}: {year_data['orders']} órdenes, ${year_data['total']:,.0f}")
        
        # 10. Resumen final
        print("\n🔟 RESUMEN FINAL")
        print("-" * 50)
        print("✅ Conexión a base de datos: EXITOSA")
        print("✅ Análisis de calidad: COMPLETADO")
        print("✅ Detección de duplicados: FUNCIONANDO")
        print("✅ Validación de datos: FUNCIONANDO")
        print("✅ Consultas específicas: FUNCIONANDO")
        print("✅ Logging: ACTIVO")
        
        print(f"\n📊 DATOS PROCESADOS:")
        print(f"   - Total registros: {total:,}")
        print(f"   - Duplicados: {dup_result.cleaned_records}")
        print(f"   - Registros problemáticos: {inc_result.cleaned_records}")
        print(f"   - Warnings totales: {val_result.warnings}")
        
        print("\n🎉 ¡DEMO COMPLETADO EXITOSAMENTE!")
        print("=" * 62)
        
    except Exception as e:
        print(f"❌ Error durante el demo: {e}")
        logger.error(f"Error en demo: {e}")


if __name__ == "__main__":
    demo_completo()
