# Guía de Conexión con Power BI

## 📊 Conectar tu Base de Datos con Power BI

### **Paso 1: Iniciar la Aplicación Web**
```bash
python web_app.py
```
La aplicación estará disponible en: `http://localhost:5000`

### **Paso 2: URLs para Power BI**

#### **Datos Completos de Órdenes:**
```
http://localhost:5000/api/powerbi/orders
```

#### **Resumen de Datos:**
```
http://localhost:5000/api/powerbi/summary
```

### **Paso 3: Configuración en Power BI**

1. **Abrir Power BI Desktop**
2. **Seleccionar "Obtener datos"**
3. **Elegir "Web" como fuente**
4. **Pegar la URL correspondiente:**
   - Para datos completos: `http://localhost:5000/api/powerbi/orders`
   - Para resumen: `http://localhost:5000/api/powerbi/summary`
5. **Configurar autenticación:**
   - Seleccionar "Anónimo" (si no hay autenticación)
   - O configurar credenciales si es necesario
6. **Hacer clic en "Conectar"**
7. **Seleccionar las tablas que deseas importar**
8. **Hacer clic en "Cargar"**

### **Paso 4: Estructura de Datos**

#### **Datos de Órdenes (`/api/powerbi/orders`):**
- `order_id`: ID único de la orden
- `status`: Estado de la orden
- `customer_name`: Nombre del cliente
- `order_date`: Fecha de la orden
- `quantity`: Cantidad
- `subtotal_amount`: Monto subtotal
- `tax_rate`: Tasa de impuesto
- `shipping_cost`: Costo de envío
- `category`: Categoría del producto
- `subcategory`: Subcategoría del producto
- `year`: Año (calculado)
- `month`: Mes (calculado)
- `quarter`: Trimestre (calculado)

#### **Resumen de Datos (`/api/powerbi/summary`):**
- **category_summary**: Resumen por categoría
- **yearly_summary**: Resumen por año
- **status_summary**: Resumen por estado

### **Paso 5: Crear Visualizaciones en Power BI**

#### **Gráficos Recomendados:**

1. **Gráfico de Barras - Ventas por Categoría**
   - Eje X: `category`
   - Eje Y: `total_revenue`

2. **Gráfico de Líneas - Evolución Temporal**
   - Eje X: `year`
   - Eje Y: `total_revenue`

3. **Gráfico Circular - Distribución por Estado**
   - Valores: `order_count`
   - Leyenda: `status`

4. **Tabla - Top Clientes**
   - Filas: `customer_name`
   - Valores: `subtotal_amount`

### **Paso 6: Actualización Automática**

Para configurar la actualización automática:

1. **En Power BI Desktop:**
   - Ir a "Inicio" > "Actualizar"
   - Configurar la frecuencia de actualización

2. **En Power BI Service:**
   - Configurar la actualización programada
   - La aplicación web debe estar ejecutándose

### **Paso 7: Filtros y Segmentaciones**

#### **Filtros Útiles:**
- **Por Año**: `year`
- **Por Categoría**: `category`
- **Por Estado**: `status`
- **Por Cliente**: `customer_name`

#### **Medidas Calculadas (DAX):**

```dax
Total Revenue = SUM(orders[subtotal_amount])

Average Order Value = DIVIDE([Total Revenue], COUNTROWS(orders))

Orders Count = COUNTROWS(orders)

Revenue Growth = 
VAR CurrentYear = MAX(orders[year])
VAR PreviousYear = CurrentYear - 1
VAR CurrentRevenue = CALCULATE([Total Revenue], orders[year] = CurrentYear)
VAR PreviousRevenue = CALCULATE([Total Revenue], orders[year] = PreviousYear)
RETURN DIVIDE(CurrentRevenue - PreviousRevenue, PreviousRevenue)
```

### **Paso 8: Dashboard Completo**

#### **Elementos del Dashboard:**

1. **KPI Cards:**
   - Total de Órdenes
   - Ingresos Totales
   - Valor Promedio por Orden
   - Crecimiento Anual

2. **Visualizaciones:**
   - Gráfico de barras: Ventas por categoría
   - Gráfico de líneas: Evolución temporal
   - Gráfico circular: Distribución por estado
   - Tabla: Top 10 clientes

3. **Filtros:**
   - Segmentación por año
   - Segmentación por categoría
   - Segmentación por estado

### **Paso 9: Publicación y Compartir**

1. **Publicar en Power BI Service:**
   - Hacer clic en "Publicar"
   - Seleccionar el workspace
   - Configurar permisos

2. **Compartir Dashboard:**
   - Crear un dashboard en el servicio
   - Agregar visualizaciones
   - Compartir con usuarios específicos

### **Paso 10: Monitoreo y Mantenimiento**

#### **Verificaciones Regulares:**
- ✅ La aplicación web está ejecutándose
- ✅ La base de datos está accesible
- ✅ Los datos se actualizan correctamente
- ✅ Las visualizaciones funcionan

#### **Logs y Monitoreo:**
- Revisar logs en `logs/app.log`
- Verificar métricas de rendimiento
- Monitorear uso de la API

### **🔧 Solución de Problemas**

#### **Error de Conexión:**
- Verificar que la aplicación web esté ejecutándose
- Comprobar la URL en el navegador
- Revisar logs de la aplicación

#### **Datos No Actualizados:**
- Verificar conexión a la base de datos
- Comprobar que los datos estén disponibles
- Revisar configuración de actualización en Power BI

#### **Rendimiento Lento:**
- Optimizar consultas en la base de datos
- Implementar paginación si es necesario
- Considerar cache de datos

### **📈 Próximos Pasos**

1. **Autenticación**: Implementar autenticación para mayor seguridad
2. **Cache**: Agregar cache para mejorar rendimiento
3. **Alertas**: Configurar alertas automáticas
4. **Backup**: Implementar respaldo de datos
5. **Escalabilidad**: Considerar múltiples instancias

¡Tu dashboard de Power BI estará conectado y funcionando con datos en tiempo real!
