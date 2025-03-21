        // Funciones para manejar los modales
        function openModal(modalId) {
            try {
                document.getElementById('modal-overlay').classList.remove('hidden');
                document.getElementById(modalId).classList.remove('hidden');
            } catch (error) {
                console.error('Error al abrir el modal:', error);
            }
        }

        function closeAllModals() {
            try {
                document.getElementById('modal-overlay').classList.add('hidden');
                
                // Ocultar todos los modales
                const modals = document.querySelectorAll('#modal-overlay > div');
                modals.forEach(modal => {
                    modal.classList.add('hidden');
                });
            } catch (error) {
                console.error('Error al cerrar los modales:', error);
            }
        }

        // Configurar botones para abrir modales
        const buttons = {
            btnOpenCliente: document.getElementById('btn-open-cliente'),
            btnOpenInventario: document.getElementById('btn-open-inventario'),
            btnOpenAlquiler: document.getElementById('btn-open-alquiler'),
            btnOpenCategoria: document.getElementById('btn-open-categoria')
        };

        if (buttons.btnOpenCliente) {
            buttons.btnOpenCliente.addEventListener('click', function() {
                try {
                    openModal('modal-cliente');
                } catch (error) {
                    console.error('Error al abrir el modal de cliente:', error);
                }
            });
        }

        if (buttons.btnOpenInventario) {
            buttons.btnOpenInventario.addEventListener('click', function() {
                try {
                    openModal('modal-inventario');
                } catch (error) {
                    console.error('Error al abrir el modal de inventario:', error);
                }
            });
        }

        if (buttons.btnOpenAlquiler) {
            console.log(buttons.btnOpenAlquiler);
            buttons.btnOpenAlquiler.addEventListener('click', function() {
                try {
                    console.log('hola');
                    openModal('modal-alquiler');
                } catch (error) {
                    console.error('Error al abrir el modal de alquiler:', error);
                }
            });
        }

        if (buttons.btnOpenCategoria) {
            buttons.btnOpenCategoria.addEventListener('click', function() {
                try {
                    openModal('modal-categoria');
                } catch (error) {
                    console.error('Error al abrir el modal de categoría:', error);
                }
            });
        }

        // Configurar botones para cerrar modales
        const closeButtons = document.querySelectorAll('.modal-close');
        closeButtons.forEach(button => {
            button.addEventListener('click', function() {
                try {
                    closeAllModals();
                } catch (error) {
                    console.error('Error al cerrar el modal:', error);
                }
            });
        });

        // Cerrar modales al hacer clic fuera de ellos
        document.getElementById('modal-overlay').addEventListener('click', function(e) {
            try {
                if (e.target === this) {
                    closeAllModals();
                }
            } catch (error) {
                console.error('Error al cerrar los modales al hacer clic fuera:', error);
            }
        });

        // Función para editar categoría
        function editarCategoria(id, nombre, descripcion) {
            try {
                document.getElementById('editar_categoria_id').value = id;
                document.getElementById('editar_nombre_categoria').value = nombre;
                document.getElementById('editar_descripcion').value = descripcion;
                
                openModal('modal-editar-categoria');
            } catch (error) {
                console.error('Error al editar la categoría:', error);
            }
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