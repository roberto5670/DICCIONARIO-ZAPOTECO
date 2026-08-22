/**
 * Realiza la búsqueda de palabras en tiempo real llamando a la API de Flask
 */
async function buscarPalabra() {
    const input = document.getElementById('inputBuscador');
    const contenedor = document.getElementById('resultados');
    const query = input.value.trim();

    // Si el campo de búsqueda está vacío, limpiar la pantalla
    if (!query) {
        contenedor.innerHTML = '';
        return;
    }

    try {
        // Consultar el endpoint API con la palabra ingresada
        const respuesta = await fetch(`/api/buscar?q=${encodeURIComponent(query)}`);
        const datos = await respuesta.json();

        // Si no se encontraron resultados
        if (datos.length === 0) {
            contenedor.innerHTML = '<div class="no-results">No se encontraron palabras coincidentes.</div>';
            return;
        }

        // Generar las tarjetas para cada palabra encontrada
        contenedor.innerHTML = datos.map(item => `
            <div class="card">
                <div class="card-header">
                    <div>
                        <span class="zapoteco-term">${escapeHTML(item.zapoteco)}</span>
                        ${item.audio ? `
                            <button 
                                type="button"
                                onclick="reproducirAudio('${escapeHTML(item.audio)}')" 
                                style="background: none; border: none; cursor: pointer; font-size: 1.2rem; margin-left: 8px; vertical-align: middle;" 
                                title="Escuchar pronunciación">
                                🔊
                            </button>
                        ` : ''}
                    </div>
                    ${item.categoria ? `<span class="categoria-tag">${escapeHTML(item.categoria)}</span>` : ''}
                </div>

                <div class="traduccion">
                    <strong>Español:</strong> ${escapeHTML(item.espaniol)}
                </div>

                ${item.ejemplo_zapoteco ? `
                    <div class="ejemplo-box">
                        <div class="ejemplo-zap"><strong>Ejemplo:</strong> ${escapeHTML(item.ejemplo_zapoteco)}</div>
                        ${item.ejemplo_españiol ? `<div class="ejemplo-esp">${escapeHTML(item.ejemplo_españiol)}</div>` : ''}
                    </div>
                ` : ''}
            </div>
        `).join('');

    } catch (error) {
        console.error('Error al realizar la búsqueda:', error);
    }
}

/**
 * Reproduce el archivo de audio desde la carpeta static/audios/
 */
function reproducirAudio(nombreArchivo) {
    if (!nombreArchivo) return;
    const audio = new Audio(`/static/audios/${nombreArchivo}`);
    audio.play().catch(e => console.error("Error al reproducir el archivo de audio:", e));
}

/**
 * Función auxiliar para evitar inyección de código e interpretar adecuadamente caracteres especiales
 */
function escapeHTML(str) {
    if (!str) return '';
    return String(str).replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
}