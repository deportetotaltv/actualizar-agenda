document.addEventListener("DOMContentLoaded", function () {
    const spans = document.querySelectorAll(".t");

    spans.forEach((span, index) => {
        const texto = span.innerText.trim().toLowerCase();
        const horaExtraida = extraerHora(texto);

        if (horaExtraida) {
            const [horas, minutos] = horaExtraida;

            const ahora = new Date();
            let fechaEventoUTC = new Date(Date.UTC(
                ahora.getFullYear(),
                ahora.getMonth(),
                ahora.getDate(),
                horas - 2,
                minutos,
                0
            ));

            if (horas < 6) {
                fechaEventoUTC.setUTCDate(fechaEventoUTC.getUTCDate() + 1);
            }

            const fechaEventoColombia = new Date(fechaEventoUTC.toLocaleString("en-US", {
                timeZone: "America/Bogota"
            }));

            const horaColombiana = formatearHora12h(fechaEventoColombia);
            span.innerText = horaColombiana;
            span.setAttribute("data-fecha", fechaEventoColombia.toISOString());

            const idUnico = fechaEventoColombia.toISOString().split("T")[0] + "_" + horaColombiana + "_" + index;
            const item = span.closest("li");
            if (item) item.setAttribute("data-id", idUnico);
        }
    });

    ocultarEventosPasados();

    document.documentElement.classList.add("loaded");
    document.body.classList.remove("ocultando-eventos");
    document.body.classList.add("loaded");
});

function extraerHora(texto) {
    const regex = /(\d{1,2})[:h\.](\d{2})\s*(am|pm)?/i;
    const match = texto.match(regex);
    if (!match) return null;

    let horas = parseInt(match[1], 10);
    const minutos = parseInt(match[2], 10);
    const ampm = match[3];

    if (ampm) {
        if (ampm.toLowerCase() === "pm" && horas !== 12) horas += 12;
        if (ampm.toLowerCase() === "am" && horas === 12) horas = 0;
    }

    return [horas, minutos];
}

function formatearHora12h(fecha) {
    let horas = fecha.getHours();
    let minutos = fecha.getMinutes();
    const ampm = horas >= 12 ? "pm" : "am";
    horas = horas % 12;
    horas = horas ? horas : 12;
    minutos = minutos < 10 ? "0" + minutos : minutos;
    return `${horas}:${minutos}${ampm}`;
}

function ocultarEventosPasados() {
    const ahoraColombia = new Date(new Date().toLocaleString("en-US", { timeZone: "America/Bogota" }));
    const inicioHoy = new Date(ahoraColombia);
    inicioHoy.setHours(0, 0, 0, 0);

    const hoyStr = inicioHoy.toISOString().split("T")[0];
    const ultimaFecha = localStorage.getItem("fecha_actual");

    if (ultimaFecha !== hoyStr) {
        localStorage.clear();
        localStorage.setItem("fecha_actual", hoyStr);
    }

    document.querySelectorAll(".t").forEach((span) => {
        const fechaTexto = span.getAttribute("data-fecha");
        if (!fechaTexto) return;

        const fechaEvento = new Date(fechaTexto);
        const li = span.closest("li");
        if (!li) return;

        const idUnico = li.getAttribute("data-id");

        if (localStorage.getItem(idUnico) === "oculto") {
            li.style.display = "none";
            return;
        }

        if (fechaEvento < inicioHoy) {
            li.style.display = "none";
            localStorage.setItem(idUnico, "oculto");
            return;
        }

        const limite = new Date(fechaEvento);
        limite.setTime(limite.getTime() + 2.5 * 60 * 60 * 1000);

        if (ahoraColombia > limite) {
            li.style.display = "none";
            localStorage.setItem(idUnico, "oculto");
        }
    });
}

// 🔐 Refuerzo contra pantalla negra
function quitarPantallaNegra() {
    document.documentElement.classList.add("loaded");
    document.body.classList.remove("ocultando-eventos");
    document.body.classList.add("loaded");
}

document.addEventListener("DOMContentLoaded", quitarPantallaNegra);
window.addEventListener("load", quitarPantallaNegra);
window.addEventListener("error", quitarPantallaNegra);
setTimeout(quitarPantallaNegra, 3000);
