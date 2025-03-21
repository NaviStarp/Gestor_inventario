// Funciones para manejar los modales
function openModal(modalId) {
    document.getElementById('modal-overlay').classList.remove('hidden');
    document.getElementById(modalId).classList.remove('hidden');
}

function closeAllModals() {
    document.getElementById('modal-overlay').classList.add('hidden');
    // Ocultar todos los modales
    const modals = document.querySelectorAll('#modal-overlay > div');
    modals.forEach(modal => {
        modal.classList.add('hidden');
    });
}

// Configurar botones para abrir modales
const btnOpenCliente = document.getElementById('btn-open-cliente');
if (btnOpenCliente) {
    btnOpenCliente.addEventListener('click', function() {
        openModal('modal-cliente');
        // Cambiar el título del modal a "Nuevo Cliente"
        document.querySelector('#modal-cliente h2').textContent = "Nuevo Cliente";
        // Resetear el formulario
        document.querySelector('#modal-cliente form').reset();
        // Cambiar la acción del formulario a crear
        document.querySelector('#modal-cliente form').action = '/clientes/crear';
    });
}

const btnOpenInventario = document.getElementById('btn-open-inventario');
if (btnOpenInventario) {
    btnOpenInventario.addEventListener('click', function() {
        openModal('modal-inventario');
    });
}

const btnOpenAlquiler = document.getElementById('btn-open-alquiler');
if (btnOpenAlquiler) {
    btnOpenAlquiler.addEventListener('click', function() {
        openModal('modal-alquiler');
    });
}

const btnOpenCategoria = document.getElementById('btn-open-categoria');
if (btnOpenCategoria) {
    btnOpenCategoria.addEventListener('click', function() {
        openModal('modal-categoria');
    });
}

// Configurar botones para cerrar modales
const closeButtons = document.querySelectorAll('.modal-close');
closeButtons.forEach(button => {
    button.addEventListener('click', closeAllModals);
});

// Cerrar modales al hacer clic fuera de ellos
document.getElementById('modal-overlay').addEventListener('click', function(e) {
    if (e.target === this) {
        closeAllModals();
    }
});



// Función para editar cliente
function editar_cliente(id, nombre, email, dni, telefono, id_cliente, prioridad) {
    openModal('modal-cliente');
    
    // Cambiar el título del modal a "Editar Cliente"
    document.querySelector('#modal-cliente h2').textContent = "Editar Cliente";
    
    // Obtener los elementos del formulario correctamente usando los IDs del HTML
    const nombreInput = document.querySelector('#modal-cliente form #nombre');
    const emailInput = document.querySelector('#modal-cliente form #email');
    const dniInput = document.querySelector('#modal-cliente form #dni');
    const telefonoInput = document.querySelector('#modal-cliente form #telefono');
    const idClienteSelect = document.querySelector('#modal-cliente form #id_cliente');
    const prioridadSelect = document.querySelector('#modal-cliente form #prioridad');
    
    // Asignar valores a los campos
    if (nombreInput) nombreInput.value = nombre || '';
    if (emailInput) emailInput.value = email || '';
    if (dniInput) dniInput.value = dni || '';
    if (telefonoInput) telefonoInput.value = telefono || '';
    
    // Manejar el select de cliente superior
    if (idClienteSelect) {
        // Asegurar que no se seleccione el mismo cliente como su propio superior
        Array.from(idClienteSelect.options).forEach(option => {
            if (option.value === id) {
                option.disabled = true;
            } else {
                option.disabled = false;
            }
        });
        idClienteSelect.value = id_cliente || '';
    }
    
    // Manejar el select de prioridad
    if (prioridadSelect) {
        prioridadSelect.value = prioridad || 'Media';
    }
    
    // Asignar la acción del formulario para editar
    const form = document.querySelector('#modal-cliente form');
    if (form) {
        form.action = '/clientes/editar/' + id;
        form.method = 'POST';
    }
}

// Función para editar categoría
function editarCategoria(id, nombre, descripcion) {
    document.getElementById('editar_categoria_id').value = id;
    document.getElementById('editar_nombre_categoria').value = nombre;
    document.getElementById('editar_descripcion').value = descripcion;
    openModal('modal-editar-categoria');
}

// Función para confirmar eliminación
function confirmarEliminar(tipo, id) {
    const form = document.getElementById('form-eliminar');
    // Configurar la acción del formulario según el tipo
    if (tipo === 'categoria') {
        form.action = `/categoria/eliminar/${id}`;
    } else if (tipo === 'cliente') {
        form.action = `/cliente/eliminar/${id}`;
    } else if (tipo === 'inventario') {
        form.action = `/inventario/eliminar/${id}`;
    } else if (tipo === 'alquiler') {
        form.action = `/alquiler/eliminar/${id}`;
    }
    openModal('modal-confirmar-eliminar');
}