document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM completamente cargado. Inicializando dashboard_layout.js'); // Log de inicio
  const userButton = document.getElementById('user-button');
  const dropdown = document.getElementById('dropdown');
  const links = document.querySelectorAll('[data-section]');
  const main = document.querySelector('.main-dinamico');

  // MENÚ USUARIO
  if (userButton) {
    userButton.addEventListener('click', (e) => {
      e.stopPropagation();
      userButton.classList.toggle('active');
      dropdown.classList.toggle('show');
      console.log('Click en botón de usuario. Menú desplegable toggleado.');
    });
  } else {
    console.warn('Botón de usuario (#user-button) no encontrado.');
  }

  document.addEventListener('click', () => {
    if (dropdown && dropdown.classList.contains('show')) {
      dropdown.classList.remove('show');
      userButton.classList.remove('active');
      console.log('Click fuera, menú desplegable cerrado.');
    }
  });

  // FUNCIONALIDAD PARA ENLACES DE NAVEGACIÓN
  if (links.length > 0) {
    links.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const section = link.getAttribute('data-section');
        console.log(`Click en enlace de navegación: ${section}. Cargando sección...`);
        cargarSeccion(section);
      });
    });
  } else {
    console.warn('No se encontraron enlaces de navegación con [data-section].');
  }

  // DELEGACIÓN DE EVENTOS EN MAIN PARA ENLACES DINÁMICOS
  if (main) {
    main.addEventListener('click', (e) => {
      const target = e.target.closest('[data-section]');
      if (target) {
        e.preventDefault();
        const section = target.getAttribute('data-section');
        console.log(`Click delegado en [data-section]: ${section}. Cargando sección...`);
        cargarSeccion(section);
      }
    });
  } else {
    console.error('Contenedor principal (.main-dinamico) no encontrado. La carga dinámica de secciones no funcionará.');
  }

  // FUNCIÓN PRINCIPAL PARA CARGAR SECCIONES
  function cargarSeccion(section) {
    console.log(`Iniciando carga de sección: /${section}`);
    fetch(`/${section}`)
      .then(response => {
        console.log(`Respuesta de fetch para /${section}:`, response);
        if (!response.ok) {
          throw new Error(`Error HTTP ${response.status}: No se pudo cargar la sección: ${section}`);
        }
        return response.text();
      })
      .then(html => {
        if (main) {
          main.innerHTML = html;
          console.log(`HTML de sección /${section} insertado en .main-dinamico.`);

          // Inicializa las funciones específicas de cada sección aquí
          if (section === 'llave-virtual') {
            console.log('Sección es "llave-virtual". Llamando a prepararFormularioPin().');
            prepararFormularioPin();
          } else if (section === 'enviar-invitacion-form') { // <-- ¡NUEVA CONDICIÓN PARA INVITACIONES!
            console.log('Sección es "enviar-invitacion-form". Llamando a prepararFormularioInvitacion().');
            prepararFormularioInvitacion(); // <-- ¡LLAMADA A LA FUNCIÓN FALTANTE!
          } else if (section === 'borrar-usuario') {
            console.log('Sección es "borrar-usuario". Llamando a prepararFormularioBorrarUsuario().');
            prepararFormularioBorrarUsuario();
          }
          // Agrega más 'else if' para otras secciones
        } else {
          console.error('No se pudo insertar HTML: .main-dinamico es nulo.');
        }
      })
      .catch(error => {
        console.error(`Error al cargar la sección /${section}:`, error);
        if (main) {
          main.innerHTML = `<p>Error al cargar la sección: ${error.message}</p>`;
        }
      });
  }

  // PREPARAR EL FORMULARIO DEL PIN
  function prepararFormularioPin() {
    console.log('Iniciando preparación del formulario PIN.');
    const form = document.getElementById('pin-form');
    const mensaje = document.getElementById('mensaje');
    const qrContainer = document.getElementById('qr-container');

    if (!form) {
      console.error("ERROR: Formulario PIN (#pin-form) no encontrado en el DOM. Revisa el HTML cargado.");
      return;
    }
    console.log('Formulario PIN encontrado:', form);

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      console.log('Evento submit del formulario PIN detectado.');
      mensaje.textContent = '';
      qrContainer.innerHTML = '';

      const formData = new FormData(form);
      const data = new URLSearchParams(formData);

      console.log('Datos del formulario antes de enviar:');
      for (let pair of formData.entries()) {
        console.log(`  ${pair[0]}: ${pair[1]}`);
      }
      console.log('Iniciando petición fetch POST a /generar-qr...');

      try {
        const res = await fetch('/generar-qr', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: data
        });

        console.log('Respuesta recibida de /generar-qr:', res);

        const resClone = res.clone();

        if (!res.ok) {
            const errorText = await resClone.text();
            console.error('Respuesta no OK de /generar-qr. Status:', res.status, 'Body:', errorText);
            try {
                const jsonError = JSON.parse(errorText);
                mensaje.className = 'error';
                mensaje.textContent = jsonError.message || 'Error desconocido del servidor.';
            } catch (jsonParseError) {
                mensaje.className = 'error';
                mensaje.textContent = `Error del servidor (status ${res.status}). No se pudo parsear la respuesta JSON.`;
                console.error('Error al parsear JSON de error:', jsonParseError);
            }
            return;
        }

        const json = await res.json();
        console.log('JSON de respuesta parseado:', json);

        if (json.status === 'ok') {
          mensaje.textContent = 'Llave virtual generada con éxito.';
          if (json.alerta) {
            mensaje.className = 'alerta';
            mensaje.textContent += ' (Alerta de seguridad activada)';
            console.warn('Alerta de seguridad activada por PIN de seguridad.');
          } else {
            mensaje.className = '';
          }
          if (json.qr) {
            let qrContent = `<img src="data:image/png;base64,${json.qr}" alt="QR generado" class="imagen-qr-mostrada" />`;
            
            // --- AQUI SE AGREGA EL ENLACE DE TEXTO DEBAJO DEL QR EN LA MISMA ASIGNACIÓN ---
            if (json.qr_link) { // Si el backend devuelve la URL que el QR codifica
                qrContent += `<p class="enlace-qr-texto">Este QR dirige a: <a href="${json.qr_link}" target="_blank">${json.qr_link}</a></p>`;
            }
            // -----------------------------------------------------------------------------
            qrContainer.innerHTML = qrContent;
            console.log('QR generado e insertado en el DOM.');
          } else {
            console.error('Respuesta OK, pero no se recibió la imagen del QR.');
            mensaje.textContent = 'Llave virtual generada, pero no se recibió la imagen del QR.';
          }
        } else {
          mensaje.className = 'error';
          mensaje.textContent = json.message || 'Error desconocido en la lógica del backend.';
          console.error('Status no "ok" en la respuesta del backend:', json.message);
        }
      } catch (error) {
        mensaje.className = 'error';
        mensaje.textContent = 'Error al generar QR: ' + error.message;
        console.error('*** Detalle del error FATAL de fetch para QR (conexión):', error);
      }
    });
  }

  // ***** FUNCIÓN PARA PREPARAR EL FORMULARIO DE INVITACIÓN - AÑADIDA AQUÍ *****
  function prepararFormularioInvitacion() {
    console.log('DEBUG: Iniciando preparación del formulario de invitación.');
    const form = document.getElementById('invitacion-form');
    const mensajeDiv = document.getElementById('mensaje-invitacion');
    const enlacePreviewDiv = document.getElementById('enlace-invitado-qr-preview');

    if (!form) {
      console.error('ERROR: Formulario de invitación (#invitacion-form) no encontrado.');
      return;
    }
    console.log('DEBUG: Formulario de invitación encontrado:', form);

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      mensajeDiv.textContent = '';
      mensajeDiv.className = '';
      enlacePreviewDiv.innerHTML = '';
      console.log('DEBUG: Evento submit del formulario de invitación detectado.');

      const formData = new FormData(form);
      const data = new URLSearchParams(formData); // URLSearchParams si no hay archivos

      console.log('DEBUG: Datos del formulario de invitación antes de enviar:');
      for (let pair of formData.entries()) {
        console.log(`  ${pair[0]}: ${pair[1]}`);
      }
      console.log('DEBUG: Iniciando petición fetch POST a /enviar-invitacion...');

      try {
        const res = await fetch('/enviar-invitacion', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded', // Correcto para URLSearchParams
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: data
        });

        console.log('DEBUG: Respuesta recibida de /enviar-invitacion:', res);

        const json = await res.json();
        console.log('DEBUG: JSON de respuesta parseado:', json);

        if (res.ok && json.status === 'ok') {
          mensajeDiv.className = 'exito';
          mensajeDiv.textContent = json.message;
          if (json.enlace_invitado) {
            enlacePreviewDiv.innerHTML = `<p>Enlace de invitación (para depuración): <a href="${json.enlace_invitado}" target="_blank">${json.enlace_invitado}</a></p>`;
          }
          console.log('Invitación enviada con éxito.');
        } else {
          mensajeDiv.className = 'error';
          mensajeDiv.textContent = json.message || 'Error desconocido al enviar invitación.';
          console.error('ERROR: Status no "ok" en la respuesta del backend para invitación:', json.message);
        }
      } catch (error) {
        mensajeDiv.className = 'error';
        mensajeDiv.textContent = 'Error al enviar invitación: ' + error.message;
        console.error('*** ERROR FATAL de fetch para invitación (conexión):', error);
      }
    });
  }

  // PREPARAR EL FORMULARIO DE BORRAR USUARIO
  function prepararFormularioBorrarUsuario() {
    const form = document.getElementById('form-borrar-usuario');
    if (form) {
      console.log("✅ Formulario de borrar-usuario detectado. Agregando listener...");
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        console.log("🔍 Submit detectado en borrar-usuario");
        const termino = document.getElementById('termino_busqueda').value;
        console.log('Término de búsqueda para borrar-usuario:', termino);

        fetch('/borrar-usuario', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
          },
          body: new URLSearchParams({ 'termino_busqueda': termino })
        })
        .then(response => {
            console.log('Respuesta recibida para borrar-usuario:', response);
            if (!response.ok) {
                throw new Error(`Error HTTP ${response.status} al borrar usuario.`);
            }
            return response.text();
        })
        .then(html => {
          const contenedorResultados = document.getElementById('resultado-usuarios');
          if (contenedorResultados) {
            contenedorResultados.innerHTML = html;
            console.log('Resultados de borrar-usuario insertados.');
          }
        })
        .catch(error => {
            console.error('Error al borrar usuario:', error);
        });
      });
    } else {
      console.log('Formulario de borrar-usuario no encontrado. No se inicializa.');
    }
  }
}); 