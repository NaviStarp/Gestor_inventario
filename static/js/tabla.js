// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar edición inline
    inicializarEdicionInline();
});


// Inicializar modal de confirmación
function inicializarModalConfirmacion() {
    const modal = document.getElementById('modal-confirmar-eliminar');
    const cancelarBtn = document.getElementById('cancelar-eliminar');
    
    if (cancelarBtn) {
        cancelarBtn.addEventListener('click', function() {
            modal.classList.add('hidden');
        });
    }
    
    // Cerrar modal al hacer clic fuera
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });
    
    // Cerrar modal con tecla ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
            modal.classList.add('hidden');
        }
    });
}

// Función para ordenar tabla
function sortTable(columnIndex) {
    const table = document.querySelector('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    // Obtener dirección de ordenamiento actual o establecer ascendente por defecto
    const headers = table.querySelectorAll('th');
    const header = headers[columnIndex + 1]; // +1 para compensar la columna de checkbox
    const currentDirection = header.dataset.sort || 'asc';
    const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
    
    // Actualizar indicador visual en encabezados
    headers.forEach(h => {
        const icon = h.querySelector('i.fas');
        if (icon) icon.className = 'fas fa-sort ml-1';
    });
    
    const icon = header.querySelector('i.fas');
    if (icon) {
        icon.className = `fas fa-sort-${newDirection === 'asc' ? 'up' : 'down'} ml-1`;
    }
    
    // Guardar nueva dirección
    header.dataset.sort = newDirection;
    
    // Ordenar filas
    rows.sort((a, b) => {
        // Obtener valores de celda para comparar
        let aValue, bValue;
        
        // Obtener el contenido de texto del span dentro de la celda correspondiente
        const aCell = a.querySelectorAll('td')[columnIndex + 1]; // +1 para compensar checkbox
        const bCell = b.querySelectorAll('td')[columnIndex + 1];
        
        if (columnIndex === 0) { // Columna numérica (Número)
            aValue = parseInt(aCell.textContent.trim()) || 0;
            bValue = parseInt(bCell.textContent.trim()) || 0;
        } else if (columnIndex === 5) { // Columna de estado
            // Orden personalizado para estados
            const estados = ['Disponible', 'En uso', 'Revisión', 'Baja'];
            aValue = estados.indexOf(aCell.querySelector('button').dataset.estado);
            bValue = estados.indexOf(bCell.querySelector('button').dataset.estado);
        } else {
            // Para el resto de columnas, comparar como texto
            aValue = aCell.textContent.trim().toLowerCase();
            bValue = bCell.textContent.trim().toLowerCase();
        }
        
        // Comparar valores según dirección
        if (newDirection === 'asc') {
            return aValue > bValue ? 1 : -1;
        } else {
            return aValue < bValue ? 1 : -1;
        }
    });
    
    // Reordenar filas en la tabla
    rows.forEach(row => tbody.appendChild(row));
    
    // Animar brevemente para indicar que se ha realizado el ordenamiento
    tbody.classList.add('opacity-50');
    setTimeout(() => tbody.classList.remove('opacity-50'), 300);
}

// Inicializar paginación
function inicializarPaginacion() {
    const itemsPerPageSelector = document.getElementById('items-per-page');
    const prevPageBtn = document.getElementById('prev-page');
    const nextPageBtn = document.getElementById('next-page');
    const pageNumbersContainer = document.getElementById('page-numbers');
    
    if (!itemsPerPageSelector || !prevPageBtn || !nextPageBtn || !pageNumbersContainer) return;
    
    let currentPage = 1;
    let itemsPerPage = parseInt(itemsPerPageSelector.value);
    const rows = document.querySelectorAll('tbody tr');
    
    // Función para mostrar página actual
    function showPage(page) {
        const startIndex = (page - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        
        // Ocultar/mostrar filas según paginación
        rows.forEach((row, index) => {
            row.classList.toggle('hidden', index < startIndex || index >= endIndex);
        });
        
        // Actualizar botones de navegación
        prevPageBtn.disabled = page === 1;
        prevPageBtn.classList.toggle('opacity-50', page === 1);
        
        const maxPage = Math.ceil(rows.length / itemsPerPage);
        nextPageBtn.disabled = page === maxPage;
        nextPageBtn.classList.toggle('opacity-50', page === maxPage);
        
        // Actualizar números de página
        updatePageNumbers(page, maxPage);
        
        // Guardar página actual
        currentPage = page;
    }
    
    // Función para actualizar números de página
    function updatePageNumbers(currentPage, maxPage) {
        pageNumbersContainer.innerHTML = '';
        
        // Determinar qué números de página mostrar
        let startPage = Math.max(1, currentPage - 2);
        let endPage = Math.min(maxPage, startPage + 4);
        
        // Ajustar si estamos cerca del final
        if (endPage - startPage < 4 && startPage > 1) {
            startPage = Math.max(1, endPage - 4);
        }
        
        // Mostrar primera página si estamos lejos
        if (startPage > 1) {
            addPageButton(1);
            if (startPage > 2) {
                addEllipsis();
            }
        }
        
        // Mostrar páginas intermedias
        for (let i = startPage; i <= endPage; i++) {
            addPageButton(i);
        }
        
        // Mostrar última página si estamos lejos
        if (endPage < maxPage) {
            if (endPage < maxPage - 1) {
                addEllipsis();
            }
            addPageButton(maxPage);
        }
    }
    
    // Función para agregar botón de página
    function addPageButton(pageNum) {
        const button = document.createElement('button');
        button.textContent = pageNum;
        button.className = pageNum === currentPage 
            ? 'bg-green-600 text-white px-3 py-1 rounded' 
            : 'bg-gray-700 hover:bg-gray-600 text-white px-3 py-1 rounded';
        button.addEventListener('click', () => showPage(pageNum));
        pageNumbersContainer.appendChild(button);
    }
    
    // Función para agregar ellipsis
    function addEllipsis() {
        const span = document.createElement('span');
        span.textContent = '...';
        span.className = 'text-white px-2 py-1';
        pageNumbersContainer.appendChild(span);
    }
    
    // Configurar eventos
    itemsPerPageSelector.addEventListener('change', function() {
        itemsPerPage = parseInt(this.value);
        showPage(1); // Volver a primera página al cambiar items por página
    });
    
    prevPageBtn.addEventListener('click', function() {
        if (currentPage > 1) {
            showPage(currentPage - 1);
        }
    });
    
    nextPageBtn.addEventListener('click', function() {
        const maxPage = Math.ceil(rows.length / itemsPerPage);
        if (currentPage < maxPage) {
            showPage(currentPage + 1);
        }
    });
    
    // Mostrar primera página inicialmente
    showPage(1);
}

// Función para mostrar notificaciones toast
function mostrarNotificacion(mensaje, tipo = 'info') {
    // Crear elemento de notificación si no existe
    let notificacionesContainer = document.getElementById('notificaciones-container');
    
    if (!notificacionesContainer) {
        notificacionesContainer = document.createElement('div');
        notificacionesContainer.id = 'notificaciones-container';
        notificacionesContainer.className = 'fixed bottom-4 right-4 z-50 flex flex-col space-y-2';
        document.body.appendChild(notificacionesContainer);
    }
    
    // Crear notificación
    const notificacion = document.createElement('div');
    notificacion.className = 'rounded-lg shadow-lg px-4 py-3 flex items-center transition-all duration-300 transform translate-x-full';
    
    // Definir clases y icono según tipo
    let iconClass, bgClass;
    switch (tipo) {
        case 'success':
            iconClass = 'fa-check-circle text-green-200';
            bgClass = 'bg-green-600';
            break;
        case 'error':
            iconClass = 'fa-exclamation-circle text-red-200';
            bgClass = 'bg-red-600';
            break;
        case 'warning':
            iconClass = 'fa-exclamation-triangle text-yellow-200';
            bgClass = 'bg-yellow-600';
            break;
        default: // info
            iconClass = 'fa-info-circle text-blue-200';
            bgClass = 'bg-blue-600';
    }
    
    notificacion.className += ` ${bgClass} text-white`;
    
    // Crear contenido
    notificacion.innerHTML = `
        <i class="fas ${iconClass} mr-2"></i>
        <span>${mensaje}</span>
        <button class="ml-4 focus:outline-none">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Agregar al contenedor
    notificacionesContainer.appendChild(notificacion);
    
    // Animar entrada
    setTimeout(() => {
        notificacion.classList.remove('translate-x-full');
    }, 10);
    
    // Configurar botón de cierre
    const closeBtn = notificacion.querySelector('button');
    closeBtn.addEventListener('click', () => {
        cerrarNotificacion(notificacion);
    });
    
    // Auto cerrar después de 5 segundos
    setTimeout(() => {
        cerrarNotificacion(notificacion);
    }, 5000);
}

// Función para cerrar notificación con animación
function cerrarNotificacion(notificacion) {
    notificacion.classList.add('opacity-0', '-translate-y-2');
    setTimeout(() => {
        notificacion.remove();
    }, 300);
}

// Función para la edición inline de campos
function inicializarEdicionInline() {
    // Seleccionar todos los elementos con clase 'editable'
    const editables = document.querySelectorAll('.editable');
    
    editables.forEach(editable => {
        // Agregar evento de clic para iniciar edición
        editable.addEventListener('click', function() {
            // Verificar si ya está en modo edición
            if (this.getAttribute('contenteditable') === 'true') return;
            
            // Obtener datos del elemento
            const id = this.dataset.id;
            const field = this.dataset.field;
            const originalValue = this.dataset.value;
            
            // Activar modo edición
            this.setAttribute('contenteditable', 'true');
            this.classList.add('bg-gray-700', 'focus:outline-none', 'focus:ring-2', 'focus:ring-green-500','border','border-green');
            this.focus();
            
            // Seleccionar todo el texto
            const range = document.createRange();
            range.selectNodeContents(this);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            
            // Función para salir del modo edición
            const finishEditing = () => {
                this.setAttribute('contenteditable', 'false');
                this.classList.remove('bg-gray-700', 'focus:outline-none', 'focus:ring-2', 'focus:ring-green-500','border','border-green');
            };
            
            // Evento para guardar al perder foco
            this.addEventListener('blur', function onBlur() {
                const newValue = this.textContent.trim();
                
                // Si el valor ha cambiado, enviar al servidor
                if (newValue !== originalValue) {
                    actualizarCampo(id, field, newValue);
                    this.dataset.value = newValue;
                } else {
                    // Restaurar valor original si no cambió
                    this.textContent = originalValue;
                }
                
                finishEditing();
                this.removeEventListener('blur', onBlur);
            });
            
            // Eventos de teclado
            this.addEventListener('keydown', function onKeydown(event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    this.blur();
                } else if (event.key === 'Escape') {
                    event.preventDefault();
                    this.textContent = originalValue;
                    this.blur();
                } 
                else if (event.key === 'Tab' && event.shiftKey) {
                    event.preventDefault();
                    
                    // Buscar elemento editable anterior
                    const allEditables = Array.from(document.querySelectorAll('.editable'));
                    const currentIndex = allEditables.indexOf(this);
                    const prevEditable = allEditables[currentIndex - 1] || allEditables[allEditables.length - 1];
                    
                    this.blur();
                    prevEditable.click();
                }
                else if (event.key === 'Tab') {
                    event.preventDefault();
                    
                    // Buscar siguiente elemento editable
                    const allEditables = Array.from(document.querySelectorAll('.editable'));
                    const currentIndex = allEditables.indexOf(this);
                    const nextEditable = allEditables[currentIndex + 1] || allEditables[0];
                    
                    this.blur();
                    nextEditable.click();
                } 
            });
        });
    });
}

// Función para actualizar campo en el servidor
function actualizarCampo(id, campo, valor) {
    // Mostrar indicador de carga
    mostrarNotificacion('Actualizando...', 'info');
    
    // Enviar datos al servidor mediante fetch
    fetch(`/producto/actualizar/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            campo: campo,
            valor: valor
        })
    })
    .then(response => {
        if (response.ok) {
            mostrarNotificacion('Campo actualizado correctamente', 'success');
        } else {
            mostrarNotificacion('Error al actualizar el campo', 'error');
            throw new Error('Error al actualizar');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarNotificacion('Error de conexión', 'error');
    });
}

// Inicializar botones de estado
function inicializarBotonesEstado() {
    const botonesEstado = document.querySelectorAll('.estado-btn');
    
    botonesEstado.forEach(boton => {
        boton.addEventListener('click', function() {
            const id = this.dataset.id;
            let estado = this.dataset.estado;
            
            // Ciclo de estados
            switch (estado) {
                case 'Disponible':
                    estado = 'En uso';
                    this.className = 'estado-btn px-3 py-1 rounded-full min-w-24 font-medium transition-colors duration-150 flex items-center justify-center bg-blue-500 hover:bg-blue-600 text-white';
                    break;
                case 'En uso':
                    estado = 'Revisión';
                    this.className = 'estado-btn px-3 py-1 rounded-full min-w-24 font-medium transition-colors duration-150 flex items-center justify-center bg-yellow-500 hover:bg-yellow-600 text-white';
                    break;
                case 'Revisión':
                    estado = 'Baja';
                    this.className = 'estado-btn px-3 py-1 rounded-full min-w-24 font-medium transition-colors duration-150 flex items-center justify-center bg-red-500 hover:bg-red-600 text-white';
                    break;
                case 'Baja':
                    estado = 'Disponible';
                    this.className = 'estado-btn px-3 py-1 rounded-full min-w-24 font-medium transition-colors duration-150 flex items-center justify-center bg-green-500 hover:bg-green-600 text-white';
                    break;
            }
            
            // Actualizar texto y dataset
            this.querySelector('span').textContent = estado;
            this.dataset.estado = estado;
            
            // Agregar animación temporal de rotación al ícono
            const icon = this.querySelector('i');
            icon.classList.add('animate-spin');
            setTimeout(() => icon.classList.remove('animate-spin'), 500);
            
            // Enviar actualización al servidor
            actualizarEstadoProducto(id, estado);
        });
    });
}

// Función para actualizar estado en el servidor
function actualizarEstadoProducto(id, estado) {
    // Buscar todos los datos necesarios para la actualización
    const fila = document.querySelector(`.estado-btn[data-id="${id}"]`).closest('tr');
    const numero = fila.querySelector('[data-field="numero"]').textContent.trim();
    const marca = fila.querySelector('[data-field="marca"]').textContent.trim();
    const modelo = fila.querySelector('[data-field="modelo"]').textContent.trim();
    const ubicacion = fila.querySelector('[data-field="ubicacion"]').textContent.trim();
    const observacion = fila.querySelector('[data-field="observacion"]').textContent.trim();
    const numero_serie_f = fila.querySelector('[data-field="numero_serie_f"]').textContent.trim();
    const numero_serie_i = fila.querySelector('[data-field="numero_serie_i"]').textContent.trim();
    
    // Valores que no se pueden obtener directamente de la fila pero son necesarios
    const categoria_id = fila.dataset.categoriaId;
    const cliente = fila.dataset.clienteId || '';
    const tipo = fila.querySelector('[data-field="tipo"]').textContent.trim();
    
    fetch(`/inventario/editar/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            numero,
            marca,
            modelo,
            estado,
            ubicacion,
            observacion,
            numero_serie_f,
            numero_serie_i,
            categoria_id,
            cliente,
            tipo
        })
    })
    .then(response => {
        if (!response.ok) {
            mostrarNotificacion('Error al actualizar el estado', 'error');
            console.error('Error al actualizar el estado');
        } else {
            mostrarNotificacion(`Estado actualizado a: ${estado}`, 'success');
        }
    })
    .catch(error => {
        mostrarNotificacion('Error de conexión', 'error');
        console.error('Error de red:', error);
    });
}

// Función para inicializar selección múltiple
function inicializarSeleccion() {
    const selectAll = document.getElementById('select-all');
    const rowCheckboxes = document.querySelectorAll('.row-checkbox');
    
    // Evento para "seleccionar todos"
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            const isChecked = this.checked;
            rowCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
                
                // Resaltar fila si está seleccionada
                const row = checkbox.closest('tr');
                if (isChecked) {
                    row.classList.add('bg-green-900', 'bg-opacity-20');
                } else {
                    row.classList.remove('bg-green-900', 'bg-opacity-20');
                }
            });
            
            // Mostrar/ocultar botón de acciones masivas
            actualizarAccionesMasivas();
        });
    }
    
    // Eventos para checkboxes individuales
    rowCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            // Resaltar fila si está seleccionada
            const row = this.closest('tr');
            if (this.checked) {
                row.classList.add('bg-green-900', 'bg-opacity-20');
            } else {
                row.classList.remove('bg-green-900', 'bg-opacity-20');
            }
            
            // Verificar si todos están seleccionados para actualizar "select all"
            if (selectAll) {
                const allChecked = Array.from(rowCheckboxes).every(cb => cb.checked);
                selectAll.checked = allChecked;
            }
            
            // Mostrar/ocultar botón de acciones masivas
            actualizarAccionesMasivas();
        });
    });
}

// Función para mostrar/ocultar botones de acciones masivas
function actualizarAccionesMasivas() {
    const rowCheckboxes = document.querySelectorAll('.row-checkbox');
    const accionesMasivasDiv = document.getElementById('borrar_seleccionados');
    
    if (!accionesMasivasDiv) return;
    
    // Comprobar si hay al menos una fila seleccionada
    const algunoSeleccionado = Array.from(rowCheckboxes).some(cb => cb.checked);
    
    if (algunoSeleccionado) {
        // Mostrar acciones masivas
        if (!document.getElementById('eliminar-seleccionados')) {
            // Crear botón de eliminar seleccionados si no existe
            const deleteButton = document.createElement('button');
            deleteButton.id = 'eliminar-seleccionados';
            deleteButton.className = 'bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline flex items-center ml-2';
            deleteButton.innerHTML = '<i class="fas fa-trash mr-2"></i>Eliminar seleccionados (<span id="contador-seleccionados">0</span>)';
            deleteButton.addEventListener('click', eliminarSeleccionados);
            accionesMasivasDiv.appendChild(deleteButton);
        }
        
        // Actualizar contador
        const contador = Array.from(rowCheckboxes).filter(cb => cb.checked).length;
        const contadorElemento = document.getElementById('contador-seleccionados');
        if (contadorElemento) {
            contadorElemento.textContent = contador;
        }
    } else {
        // Ocultar acciones masivas
        const eliminarBtn = document.getElementById('eliminar-seleccionados');
        if (eliminarBtn) {
            eliminarBtn.remove();
        }
    }
}