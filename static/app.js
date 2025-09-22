/**
 * JavaScript para la aplicación web de gestión de datos
 */

// Variables globales
let currentPage = 1;
let currentFilters = {};

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    loadOrders();
});

// Variables globales para gestión de órdenes
let currentEditingOrderId = null;

// Navegación
function showSection(sectionName) {
    // Ocultar todas las secciones
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Remover clase active de todos los nav-links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Mostrar sección seleccionada
    document.getElementById(sectionName + '-section').style.display = 'block';
    
    // Agregar clase active al nav-link correspondiente
    event.target.classList.add('active');
    
    // Actualizar título
    const titles = {
        'dashboard': 'Dashboard',
        'data-quality': 'Calidad de Datos',
        'data-cleaning': 'Limpieza de Datos',
        'orders': 'Gestión de Órdenes',
        'order-management': 'Gestión de Órdenes',
        'powerbi': 'Power BI',
        'export': 'Exportar Datos'
    };
    document.getElementById('page-title').textContent = titles[sectionName];
    
    // Cargar datos específicos de la sección
    if (sectionName === 'data-quality') {
        loadDataQualityReport();
    } else if (sectionName === 'order-management') {
        setupOrderManagement();
    }
}

// Dashboard
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();
        
        // Actualizar estadísticas
        document.getElementById('total-orders').textContent = data.total_orders.toLocaleString();
        document.getElementById('completed-orders').textContent = data.status_distribution['Order Finished'] || 0;
        document.getElementById('duplicates').textContent = '2'; // Se actualizará con la verificación
        document.getElementById('categories').textContent = Object.keys(data.category_distribution).length;
        
        // Crear gráficos
        createStatusChart(data.status_distribution);
        createCategoryChart(data.category_revenue);
        createYearlyChart(data.yearly_stats);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showAlert('Error al cargar datos del dashboard', 'danger');
    }
}

function createStatusChart(statusData) {
    const ctx = document.getElementById('statusChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(statusData),
            datasets: [{
                data: Object.values(statusData),
                backgroundColor: [
                    '#28a745',
                    '#ffc107',
                    '#dc3545'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function createCategoryChart(categoryData) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(categoryData),
            datasets: [{
                label: 'Ingresos ($)',
                data: Object.values(categoryData),
                backgroundColor: [
                    '#007bff',
                    '#28a745',
                    '#ffc107'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function createYearlyChart(yearlyData) {
    const ctx = document.getElementById('yearlyChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: yearlyData.map(item => item.year),
            datasets: [{
                label: 'Órdenes',
                data: yearlyData.map(item => item.orders),
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                tension: 0.4
            }, {
                label: 'Ingresos ($)',
                data: yearlyData.map(item => item.revenue),
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                tension: 0.4,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false,
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

// Calidad de Datos
async function loadDataQualityReport() {
    const loading = document.querySelector('#data-quality-section .loading');
    const report = document.getElementById('quality-report');
    
    loading.style.display = 'block';
    report.innerHTML = '';
    
    try {
        const response = await fetch('/api/data-quality/report');
        const data = await response.json();
        
        loading.style.display = 'none';
        
        const html = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Estadísticas Generales</h6>
                    <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Total de Registros:</span>
                            <span class="badge bg-primary">${data.total_records.toLocaleString()}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Total de Columnas:</span>
                            <span class="badge bg-primary">${data.total_columns}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between">
                            <span>Registros Duplicados:</span>
                            <span class="badge bg-warning">${data.duplicate_records}</span>
                        </li>
                    </ul>
                </div>
                <div class="col-md-6">
                    <h6>Completitud de Datos</h6>
                    <ul class="list-group">
                        ${Object.entries(data.data_completeness).map(([column, percentage]) => `
                            <li class="list-group-item d-flex justify-content-between">
                                <span>${column}:</span>
                                <span class="badge ${percentage === 100 ? 'bg-success' : 'bg-warning'}">${percentage}%</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
        
        report.innerHTML = html;
        
    } catch (error) {
        loading.style.display = 'none';
        report.innerHTML = '<div class="alert alert-danger">Error al cargar el reporte de calidad</div>';
        console.error('Error loading data quality report:', error);
    }
}

// Limpieza de Datos
async function checkDuplicates() {
    showLoading('cleaning-results');
    
    try {
        const response = await fetch('/api/data-cleaning/duplicates');
        const data = await response.json();
        
        const html = `
            <div class="card mt-3">
                <div class="card-header">
                    <h6><i class="fas fa-copy me-2"></i>Resultados de Verificación de Duplicados</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-warning">${data.duplicates_found}</h4>
                                <p class="mb-0">Duplicados Encontrados</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-info">${data.total_records}</h4>
                                <p class="mb-0">Total Registros</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-warning">${data.warnings}</h4>
                                <p class="mb-0">Warnings</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-success">${data.total_records - data.duplicates_found}</h4>
                                <p class="mb-0">Registros Únicos</p>
                            </div>
                        </div>
                    </div>
                    ${data.duplicates_found > 0 ? `
                        <div class="mt-3">
                            <h6>Ejemplos de Duplicados:</h6>
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Cliente</th>
                                            <th>Fecha</th>
                                            <th>Categoría</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${data.summary.duplicate_examples ? data.summary.duplicate_examples.map(dup => `
                                            <tr>
                                                <td>${dup.order_id}</td>
                                                <td>${dup.customer_name}</td>
                                                <td>${dup.order_date}</td>
                                                <td>${dup.category}</td>
                                            </tr>
                                        `).join('') : '<tr><td colspan="4">No hay ejemplos disponibles</td></tr>'}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    ` : '<div class="alert alert-success mt-3">¡No se encontraron duplicados!</div>'}
                </div>
            </div>
        `;
        
        document.getElementById('cleaning-results').innerHTML = html;
        
    } catch (error) {
        document.getElementById('cleaning-results').innerHTML = '<div class="alert alert-danger">Error al verificar duplicados</div>';
        console.error('Error checking duplicates:', error);
    }
}

async function checkIncomplete() {
    showLoading('cleaning-results');
    
    try {
        const response = await fetch('/api/data-cleaning/incomplete');
        const data = await response.json();
        
        const html = `
            <div class="card mt-3">
                <div class="card-header">
                    <h6><i class="fas fa-exclamation-circle me-2"></i>Resultados de Verificación de Registros Incompletos</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-danger">${data.incomplete_records}</h4>
                                <p class="mb-0">Registros Problemáticos</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-danger">${data.errors}</h4>
                                <p class="mb-0">Errores</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-warning">${data.warnings}</h4>
                                <p class="mb-0">Warnings</p>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="text-center">
                                <h4 class="text-success">${data.total_records - data.incomplete_records}</h4>
                                <p class="mb-0">Registros Válidos</p>
                            </div>
                        </div>
                    </div>
                    ${data.incomplete_records > 0 ? `
                        <div class="mt-3">
                            <h6>Problemas Encontrados:</h6>
                            <div class="alert alert-warning">
                                <strong>IDs de registros problemáticos:</strong> 
                                ${data.summary.problematic_order_ids ? data.summary.problematic_order_ids.join(', ') : 'No disponibles'}
                            </div>
                        </div>
                    ` : '<div class="alert alert-success mt-3">¡No se encontraron registros incompletos!</div>'}
                </div>
            </div>
        `;
        
        document.getElementById('cleaning-results').innerHTML = html;
        
    } catch (error) {
        document.getElementById('cleaning-results').innerHTML = '<div class="alert alert-danger">Error al verificar registros incompletos</div>';
        console.error('Error checking incomplete records:', error);
    }
}

async function validateData() {
    showLoading('cleaning-results');
    
    try {
        const response = await fetch('/api/data-cleaning/validate');
        const data = await response.json();
        
        const html = `
            <div class="card mt-3">
                <div class="card-header">
                    <h6><i class="fas fa-check-circle me-2"></i>Resultados de Validación de Tipos de Datos</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-4">
                            <div class="text-center">
                                <h4 class="text-danger">${data.errors}</h4>
                                <p class="mb-0">Errores</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="text-center">
                                <h4 class="text-warning">${data.warnings}</h4>
                                <p class="mb-0">Warnings</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="text-center">
                                <h4 class="text-success">${data.total_records - data.warnings - data.errors}</h4>
                                <p class="mb-0">Registros Válidos</p>
                            </div>
                        </div>
                    </div>
                    ${data.warnings > 0 ? `
                        <div class="mt-3">
                            <h6>Problemas de Validación:</h6>
                            <ul class="list-group">
                                ${data.summary.validation_issues ? data.summary.validation_issues.map(issue => `
                                    <li class="list-group-item">${issue}</li>
                                `).join('') : '<li class="list-group-item">No hay detalles disponibles</li>'}
                            </ul>
                        </div>
                    ` : '<div class="alert alert-success mt-3">¡Todos los datos pasaron la validación!</div>'}
                </div>
            </div>
        `;
        
        document.getElementById('cleaning-results').innerHTML = html;
        
    } catch (error) {
        document.getElementById('cleaning-results').innerHTML = '<div class="alert alert-danger">Error al validar datos</div>';
        console.error('Error validating data:', error);
    }
}

// Gestión de Órdenes
async function loadOrders(page = 1) {
    const status = document.getElementById('status-filter').value;
    const category = document.getElementById('category-filter').value;
    
    currentFilters = { status, category };
    currentPage = page;
    
    const params = new URLSearchParams({
        page: page,
        per_page: 50,
        ...(status && { status }),
        ...(category && { category })
    });
    
    try {
        const response = await fetch(`/api/orders?${params}`);
        const data = await response.json();
        
        // Actualizar tabla
        const tbody = document.getElementById('orders-table');
        if (data.orders.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No se encontraron órdenes</td></tr>';
        } else {
            tbody.innerHTML = data.orders.map(order => `
                <tr>
                    <td>${order.order_id}</td>
                    <td>${order.customer_name}</td>
                    <td>${new Date(order.order_date).toLocaleDateString()}</td>
                    <td><span class="badge bg-${getStatusColor(order.status)}">${order.status}</span></td>
                    <td>${order.category}</td>
                    <td>$${parseFloat(order.subtotal_amount).toLocaleString()}</td>
                    <td>${order.quantity}</td>
                </tr>
            `).join('');
        }
        
        // Actualizar paginación
        updatePagination(data.total_pages, page);
        
    } catch (error) {
        console.error('Error loading orders:', error);
        document.getElementById('orders-table').innerHTML = '<tr><td colspan="7" class="text-center text-danger">Error al cargar órdenes</td></tr>';
    }
}

function filterOrders() {
    loadOrders(1);
}

function updatePagination(totalPages, currentPage) {
    const pagination = document.getElementById('pagination');
    let html = '';
    
    // Botón anterior
    html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="loadOrders(${currentPage - 1})">Anterior</a>
    </li>`;
    
    // Páginas
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        html += `<li class="page-item ${i === currentPage ? 'active' : ''}">
            <a class="page-link" href="#" onclick="loadOrders(${i})">${i}</a>
        </li>`;
    }
    
    // Botón siguiente
    html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="loadOrders(${currentPage + 1})">Siguiente</a>
    </li>`;
    
    pagination.innerHTML = html;
}

function getStatusColor(status) {
    const colors = {
        'Order Finished': 'success',
        'Order Returned': 'warning',
        'Order Cancelled': 'danger'
    };
    return colors[status] || 'secondary';
}

// Power BI
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    element.select();
    element.setSelectionRange(0, 99999);
    document.execCommand('copy');
    
    showAlert('URL copiada al portapapeles', 'success');
}

// Exportar
async function exportCSV() {
    try {
        const response = await fetch('/api/export/csv');
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `orders_export_${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            showAlert('Archivo CSV descargado exitosamente', 'success');
        } else {
            throw new Error('Error al exportar CSV');
        }
    } catch (error) {
        console.error('Error exporting CSV:', error);
        showAlert('Error al exportar CSV', 'danger');
    }
}

// Utilidades
function refreshData() {
    const currentSection = document.querySelector('.section[style*="block"]');
    if (currentSection) {
        const sectionId = currentSection.id;
        if (sectionId === 'dashboard-section') {
            loadDashboardData();
        } else if (sectionId === 'data-quality-section') {
            loadDataQualityReport();
        } else if (sectionId === 'orders-section') {
            loadOrders(currentPage);
        }
    }
    showAlert('Datos actualizados', 'success');
}

function showLoading(containerId) {
    document.getElementById(containerId).innerHTML = `
        <div class="text-center">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
            <p class="mt-2">Procesando...</p>
        </div>
    `;
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.top = '20px';
    alertDiv.style.right = '20px';
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// ===== GESTIÓN DE ÓRDENES =====

function setupOrderManagement() {
    // Configurar formulario de creación
    document.getElementById('create-order-form').addEventListener('submit', createOrder);
    
    // Configurar formulario de edición
    document.getElementById('edit-order-form').addEventListener('submit', updateOrder);
    
    // Establecer fecha actual por defecto
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('create-order-date').value = today;
}

async function createOrder(event) {
    event.preventDefault();
    
    const formData = {
        customer_name: document.getElementById('create-customer-name').value,
        order_date: document.getElementById('create-order-date').value,
        status: document.getElementById('create-status').value,
        quantity: parseInt(document.getElementById('create-quantity').value),
        subtotal_amount: parseFloat(document.getElementById('create-subtotal').value),
        tax_rate: parseFloat(document.getElementById('create-tax-rate').value),
        shipping_cost: parseFloat(document.getElementById('create-shipping').value),
        category: document.getElementById('create-category').value,
        subcategory: document.getElementById('create-subcategory').value
    };
    
    try {
        const response = await fetch('/api/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert(`Orden creada exitosamente con ID: ${result.order_id}`, 'success');
            document.getElementById('create-order-form').reset();
            // Actualizar dashboard si está visible
            if (document.getElementById('dashboard-section').style.display !== 'none') {
                loadDashboardData();
            }
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error creating order:', error);
        showAlert('Error al crear la orden', 'danger');
    }
}

async function searchOrder() {
    const orderId = document.getElementById('search-order-id').value;
    
    if (!orderId) {
        showAlert('Por favor ingresa un ID de orden', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`/api/orders/${orderId}`);
        const result = await response.json();
        
        if (response.ok) {
            // Llenar formulario de edición
            document.getElementById('edit-customer-name').value = result.customer_name;
            document.getElementById('edit-order-date').value = result.order_date;
            document.getElementById('edit-status').value = result.status;
            document.getElementById('edit-quantity').value = result.quantity;
            document.getElementById('edit-subtotal').value = result.subtotal_amount;
            document.getElementById('edit-tax-rate').value = result.tax_rate;
            document.getElementById('edit-shipping').value = result.shipping_cost;
            document.getElementById('edit-category').value = result.category;
            document.getElementById('edit-subcategory').value = result.subcategory;
            
            // Mostrar formulario de edición
            document.getElementById('order-edit-form').style.display = 'block';
            currentEditingOrderId = orderId;
            
            showAlert('Orden encontrada', 'success');
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
            document.getElementById('order-edit-form').style.display = 'none';
            currentEditingOrderId = null;
        }
    } catch (error) {
        console.error('Error searching order:', error);
        showAlert('Error al buscar la orden', 'danger');
    }
}

async function updateOrder(event) {
    event.preventDefault();
    
    if (!currentEditingOrderId) {
        showAlert('No hay orden seleccionada para editar', 'warning');
        return;
    }
    
    const formData = {
        customer_name: document.getElementById('edit-customer-name').value,
        order_date: document.getElementById('edit-order-date').value,
        status: document.getElementById('edit-status').value,
        quantity: parseInt(document.getElementById('edit-quantity').value),
        subtotal_amount: parseFloat(document.getElementById('edit-subtotal').value),
        tax_rate: parseFloat(document.getElementById('edit-tax-rate').value),
        shipping_cost: parseFloat(document.getElementById('edit-shipping').value),
        category: document.getElementById('edit-category').value,
        subcategory: document.getElementById('edit-subcategory').value
    };
    
    try {
        const response = await fetch(`/api/orders/${currentEditingOrderId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('Orden actualizada exitosamente', 'success');
            // Actualizar dashboard si está visible
            if (document.getElementById('dashboard-section').style.display !== 'none') {
                loadDashboardData();
            }
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error updating order:', error);
        showAlert('Error al actualizar la orden', 'danger');
    }
}

async function deleteOrder() {
    if (!currentEditingOrderId) {
        showAlert('No hay orden seleccionada para eliminar', 'warning');
        return;
    }
    
    if (!confirm(`¿Estás seguro de que quieres eliminar la orden ${currentEditingOrderId}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/orders/${currentEditingOrderId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('Orden eliminada exitosamente', 'success');
            document.getElementById('order-edit-form').style.display = 'none';
            document.getElementById('search-order-id').value = '';
            currentEditingOrderId = null;
            // Actualizar dashboard si está visible
            if (document.getElementById('dashboard-section').style.display !== 'none') {
                loadDashboardData();
            }
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error deleting order:', error);
        showAlert('Error al eliminar la orden', 'danger');
    }
}

async function bulkUpdateStatus() {
    const orderIdsText = document.getElementById('bulk-order-ids').value;
    const newStatus = document.getElementById('bulk-new-status').value;
    
    if (!orderIdsText.trim()) {
        showAlert('Por favor ingresa los IDs de las órdenes', 'warning');
        return;
    }
    
    // Parsear IDs
    const orderIds = orderIdsText.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id));
    
    if (orderIds.length === 0) {
        showAlert('No se encontraron IDs válidos', 'warning');
        return;
    }
    
    if (!confirm(`¿Estás seguro de que quieres actualizar ${orderIds.length} órdenes al estado "${newStatus}"?`)) {
        return;
    }
    
    try {
        const response = await fetch('/api/orders/bulk-status', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                order_ids: orderIds,
                status: newStatus
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert(`${result.updated_count} órdenes actualizadas exitosamente`, 'success');
            document.getElementById('bulk-order-ids').value = '';
            // Actualizar dashboard si está visible
            if (document.getElementById('dashboard-section').style.display !== 'none') {
                loadDashboardData();
            }
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        console.error('Error in bulk update:', error);
        showAlert('Error al actualizar las órdenes', 'danger');
    }
}
