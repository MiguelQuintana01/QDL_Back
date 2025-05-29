function getDomain() {
    let domain = "";
    if (window.location.origin.includes("localhost")) {
        domain = "http://localhost:8000";
    } else {
        domain = window.location.origin;
    }
    return domain;
}

if (typeof window !== 'undefined') {
    setInterval(setTimeToP, 990)
    setMetasWeights();
    setInterval(setMetasWeights, 10000)
}


async function setTimeToP() {
    if (window.location.href.includes("screen")) {
        const clocks = document.getElementsByClassName("clock");
        if (clocks.length > 0) {
            const clock = clocks[0];
            clock.innerHTML = obtenerFechaHoraFormateada();
        }
    }
}



async function setMetasWeights() {
    try {
        const lastMeta = await getLastMeta();
        setTextMeta(numberToFormat(lastMeta.meta));
        const weight = await getMetaWeight();
        setTextWeight(numberToFormat(weight));
        createChart(lastMeta, weight);
    } catch (e) {
        console.log(e)
    }
}


function obtenerFechaHoraFormateada() {
    // Crear una nueva instancia de Date para obtener la fecha y hora actual
    let now = new Date();

    // Array con los días de la semana para facilitar su obtención
    let daysOfWeek = ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'];

    // Array con los meses del año para facilitar su obtención
    let monthsOfYear = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];

    // Obtener las diferentes partes de la fecha y hora
    let dayOfWeek = daysOfWeek[now.getDay()];
    let day = String(now.getDate()).padStart(2, '0');  // Añadir cero delante si es necesario
    let month = monthsOfYear[now.getMonth()];
    let year = now.getFullYear();

    let hours = String(now.getHours()).padStart(2, '0');
    let minutes = String(now.getMinutes()).padStart(2, '0');
    let seconds = String(now.getSeconds()).padStart(2, '0');

    // Construir la cadena final en el formato deseado
    let formattedDate = `${dayOfWeek}, ${day} de ${month} de ${year} ${hours}:${minutes}:${seconds}`;

    return formattedDate;
}

async function getAllMetas() {
    const response = await fetch(getDomain() + '/api/settings/metas');
    return await response.json();
}
async function getLastMeta() {
    const metas = await getAllMetas();
    const actualHourInSeconds = (new Date().getHours()) * 3600
    let meta = {};
    for (let i = metas.dates.length - 1; i >= 0; i--) {
        if (metas.dates[i] <= actualHourInSeconds) {
            meta.date = metas.dates[i];
            meta.meta = metas.weights[i];
            meta.dateDate = unixToDates([meta.date])[0];
            break;
        }
    }
    return meta;
}
async function getLastMeta2() {
    const response = await fetch(getDomain() + '/api/metas');
    let data = await response.json();

    data.dateDate = unixToDates([data.date])[0]

    return data;
}


function setTextMeta(value) {
    document.getElementById("metaP").innerHTML = value;
}

function setTextWeight(value) {
    document.getElementById("weightP").innerHTML = value;
}

function getDateWithOutTimeUnix() {
    const ahora = new Date();
    const fechaSinTiempo = new Date(ahora.getFullYear(), ahora.getMonth(), ahora.getDate());
    const timestampUnix = Math.floor(fechaSinTiempo.getTime() / 1000);
    return timestampUnix;
}

async function getMetaWeight() {
    const period = { start: getDateWithOutTimeUnix(), gmt: getGmt() };

    const weight = await (await makePost(getDomain() + "/api/weights", period)).json();
    let lastWeightMeta = sumarice(weight.peso);

    return lastWeightMeta;
}


function unixToDates(listDates) {
    let dates = [];

    listDates.forEach((dateUnix) => {
        dates.push(new Date(dateUnix * 1000));
    });

    return dates
}


function generateForm(data) {
    let form = new FormData();

    const keys = Object.keys(data);

    keys.forEach(key => {
        form.append(key, data[key]);
    });

    return form;
}


function sumarice(nums) {
    let acumulate = 0;
    nums.forEach(actual => {
        acumulate += actual;
    });
    return acumulate;
}


function numberToFormat(value) {
    const formatedNumber = (Math.round(value * 100) / 100).toLocaleString() + "kg";
    return formatedNumber;
}



function getGmt() {
    return -(new Date().getTimezoneOffset() / 60);
}


async function makePost(url, data) {
    const params = generateForm(data);

    const response = await fetch(url, {
        method: 'POST',
        body: params,
    });

    return response;
}


async function createCanvas(width, height) {
    const canvas = document.createElement('canvas');

    canvas.id = "pieChart";
    canvas.width = width;
    canvas.height = height;

    return canvas;
}


async function createChart(lastMeta, weight) {
    if (typeof window === 'undefined') {
        return
    }
    const innerWidth = window.innerWidth;
    const innerHeight = window.innerHeight;

    const container = document.getElementById('pieContainer');
    const ctx = await createCanvas(innerWidth * .7, innerHeight * .7);
    container.innerHTML = "";
    container.appendChild(ctx);


    let metaRestant = lastMeta.meta - (weight)
    metaRestant = metaRestant >= 0 ? metaRestant : 0;

    new Chart(ctx, {
        type: 'pie',
        data: {
            datasets: [{
                data: [weight, metaRestant],
                backgroundColor: ['#36A2EB', '#ffd4a1'],
                hoverBackgroundColor: ['#36A2EB', '#ffd4a1']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 0
            }
        },
    });
}