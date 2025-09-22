"""
Script para abrir la aplicación web en el navegador.
"""
import webbrowser
import time
import requests
import sys

def check_app_running():
    """Verificar si la aplicación está ejecutándose."""
    try:
        response = requests.get("http://localhost:5000/api/dashboard/stats", timeout=5)
        return response.status_code == 200
    except:
        return False

def open_web_app():
    """Abrir la aplicación web en el navegador."""
    print("🌐 Abriendo aplicación web...")
    print("=" * 50)
    
    # Verificar si la aplicación está ejecutándose
    print("1. Verificando si la aplicación está ejecutándose...")
    if not check_app_running():
        print("❌ La aplicación no está ejecutándose")
        print("💡 Ejecuta primero: python start_web_app.py")
        return False
    
    print("✅ Aplicación ejecutándose correctamente")
    
    # URLs disponibles
    urls = {
        "Dashboard Principal": "http://localhost:5000",
        "API Dashboard Stats": "http://localhost:5000/api/dashboard/stats",
        "API Power BI Orders": "http://localhost:5000/api/powerbi/orders",
        "API Power BI Summary": "http://localhost:5000/api/powerbi/summary"
    }
    
    print("\n2. URLs disponibles:")
    for name, url in urls.items():
        print(f"   📊 {name}: {url}")
    
    # Abrir el dashboard principal
    print("\n3. Abriendo dashboard principal...")
    try:
        webbrowser.open("http://localhost:5000")
        print("✅ Dashboard abierto en el navegador")
        
        print("\n🎉 ¡Aplicación web lista!")
        print("=" * 50)
        print("📋 Funcionalidades disponibles:")
        print("   • Dashboard con estadísticas en tiempo real")
        print("   • Gestión de limpieza de datos")
        print("   • Visualización de órdenes con filtros")
        print("   • Conexión con Power BI")
        print("   • Exportación de datos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error abriendo navegador: {e}")
        print("💡 Abre manualmente: http://localhost:5000")
        return False

if __name__ == "__main__":
    open_web_app()
