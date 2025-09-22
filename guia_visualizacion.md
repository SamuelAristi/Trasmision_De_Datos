# 🌐 Guía de Visualización - Aplicación Web

## 🚀 **Cómo Acceder a tu Aplicación Web**

### **Paso 1: Iniciar la Aplicación**
```bash
python start_web_app.py
```

### **Paso 2: Abrir en el Navegador**
```bash
python open_web_app.py
```

**O manualmente:**
- Abre tu navegador web
- Ve a: **http://localhost:5000**

---

## 📊 **Navegación por la Aplicación**

### **🏠 Dashboard Principal**
**URL:** http://localhost:5000

**Lo que verás:**
- **4 tarjetas de estadísticas:**
  - Total de Órdenes: 5,499
  - Órdenes Completadas: 4,924
  - Duplicados: 2
  - Categorías: 3

- **3 gráficos interactivos:**
  - **Gráfico Circular:** Distribución por Estado
  - **Gráfico de Barras:** Ventas por Categoría
  - **Gráfico de Líneas:** Evolución Anual (2009-2012)

### **🛡️ Calidad de Datos**
**Acceso:** Clic en "Calidad de Datos" en el menú lateral

**Funcionalidades:**
- **Reporte completo** de calidad de datos
- **Completitud por columna** (100% en todos los campos)
- **Estadísticas generales** del dataset
- **Distribución de valores** por categoría

### **🧹 Limpieza de Datos**
**Acceso:** Clic en "Limpieza de Datos" en el menú lateral

**3 herramientas disponibles:**

#### **1. Verificar Duplicados**
- **Botón:** "Verificar" (amarillo)
- **Resultado:** 2 duplicados encontrados
- **Detalles:** Ejemplos específicos con IDs

#### **2. Registros Incompletos**
- **Botón:** "Verificar" (rojo)
- **Resultado:** 0 registros incompletos
- **Estado:** ✅ Todos los datos están completos

#### **3. Validar Tipos**
- **Botón:** "Verificar" (azul)
- **Resultado:** 15,455 warnings
- **Detalles:** Valores extremos identificados

### **🛒 Gestión de Órdenes**
**Acceso:** Clic en "Órdenes" en el menú lateral

**Funcionalidades:**
- **Tabla paginada** con 5,499 registros
- **Filtros dinámicos:**
  - Por Estado: Order Finished, Order Returned, Order Cancelled
  - Por Categoría: Technology, Furniture, Office Supplies
- **Navegación:** Botones Anterior/Siguiente
- **Información mostrada:**
  - ID, Cliente, Fecha, Estado, Categoría, Monto, Cantidad

### **📈 Power BI**
**Acceso:** Clic en "Power BI" en el menú lateral

**URLs para conectar:**
- **Datos Completos:** http://localhost:5000/api/powerbi/orders
- **Resumen:** http://localhost:5000/api/powerbi/summary

**Instrucciones:**
1. Copiar URL (botón de copiar)
2. En Power BI: Obtener datos → Web
3. Pegar URL
4. Configurar autenticación
5. Importar datos

### **📥 Exportar**
**Acceso:** Clic en "Exportar" en el menú lateral

**Opciones:**
- **Exportar CSV:** Descarga todos los datos
- **API Endpoints:** URLs para integración

---

## 🎯 **Funcionalidades Interactivas**

### **🔄 Actualizar Datos**
- **Botón:** "Actualizar" (esquina superior derecha)
- **Función:** Recarga datos en tiempo real
- **Indicador:** Badge verde "Conectado"

### **📱 Diseño Responsive**
- **Desktop:** Vista completa con sidebar
- **Tablet/Móvil:** Menú colapsable
- **Gráficos:** Se adaptan al tamaño de pantalla

### **🎨 Interfaz Moderna**
- **Colores:** Gradientes azul/púrpura
- **Iconos:** Font Awesome
- **Animaciones:** Hover effects en tarjetas
- **Tipografía:** Bootstrap 5

---

## 🔗 **URLs Importantes**

### **Aplicación Principal:**
- **Dashboard:** http://localhost:5000
- **API Stats:** http://localhost:5000/api/dashboard/stats

### **Power BI:**
- **Datos Órdenes:** http://localhost:5000/api/powerbi/orders
- **Resumen:** http://localhost:5000/api/powerbi/summary

### **APIs:**
- **Órdenes:** http://localhost:5000/api/orders
- **Calidad:** http://localhost:5000/api/data-quality/report
- **Duplicados:** http://localhost:5000/api/data-cleaning/duplicates
- **Exportar:** http://localhost:5000/api/export/csv

---

## 🛠️ **Solución de Problemas**

### **❌ La aplicación no se abre:**
1. Verificar que esté ejecutándose: `netstat -an | findstr :5000`
2. Reiniciar: `python start_web_app.py`
3. Verificar logs en `logs/app.log`

### **❌ Los datos no se cargan:**
1. Verificar conexión a base de datos
2. Comprobar que PostgreSQL esté ejecutándose
3. Revisar credenciales en `.env`

### **❌ Los gráficos no aparecen:**
1. Verificar conexión a internet (para Chart.js)
2. Abrir consola del navegador (F12)
3. Verificar errores JavaScript

### **❌ Power BI no conecta:**
1. Verificar que la aplicación esté ejecutándose
2. Probar URL en el navegador
3. Verificar formato JSON de respuesta

---

## 📊 **Datos que Verás**

### **Estadísticas Generales:**
- **Total Órdenes:** 5,499
- **Período:** 2009-2012
- **Estados:** Order Finished (4,924), Order Returned (572), Order Cancelled (3)
- **Categorías:** Office Supplies (3,066), Technology (1,280), Furniture (1,153)

### **Problemas Identificados:**
- **Duplicados:** 2 registros
- **Valores Extremos:** 5,049 montos > $100,000
- **Costos Altos:** 4,907 envíos > $1,000
- **Estados No Estándar:** Necesitan normalización

### **Calidad de Datos:**
- **Completitud:** 100% (sin valores nulos)
- **Integridad:** Todos los campos requeridos presentes
- **Consistencia:** Algunos valores extremos identificados

---

## 🎉 **¡Tu Dashboard Está Listo!**

**Accede ahora a:** http://localhost:5000

**Explora todas las funcionalidades:**
1. ✅ Dashboard con estadísticas
2. ✅ Limpieza de datos interactiva
3. ✅ Visualización de órdenes
4. ✅ Conexión con Power BI
5. ✅ Exportación de datos

**¡Disfruta gestionando tus datos de manera visual e interactiva!** 🚀
