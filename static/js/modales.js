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
            console.log(btnOpenAlquiler);
            btnOpenAlquiler.addEventListener('click', function() {
                console.log('hola');
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