// Aquí irá la lógica JS para inicializar y actualizar los gráficos principales y comparativos

// charts.js
// Inicialización y actualización de gráficos principales

let evolucionChart, generoChart, rankingChart;

function actualizarGraficos(kpis) {
  // Evolución de delitos por año (dummy)
  const ctxEvol = document.getElementById('evolucionChart').getContext('2d');
  if (evolucionChart) evolucionChart.destroy();
  evolucionChart = new Chart(ctxEvol, {
    type: 'line',
    data: {
      labels: ['2019', '2020', '2021', '2022', '2023'], // Reemplazar por años reales
      datasets: [{
        label: 'Delitos',
        data: [12, 19, 3, 5, 2], // Reemplazar por datos reales
        borderColor: '#ff6361', // coral
        backgroundColor: 'rgba(0,63,92,0.15)', // azul oscuro translúcido
        fill: true
      }]
    }
  });

  // Distribución de género (dummy)
  const ctxGen = document.getElementById('generoChart').getContext('2d');
  if (generoChart) generoChart.destroy();
  generoChart = new Chart(ctxGen, {
    type: 'doughnut',
    data: {
      labels: ['Mujeres', 'Hombres'],
      datasets: [{
        data: [kpis.porc_mujeres || 0, kpis.porc_hombres || 0],
        backgroundColor: ['#58508d', '#003f5c'] // violeta, azul oscuro
      }]
    }
  });

  // Ranking de partidos (dummy)
  const ctxRank = document.getElementById('rankingChart').getContext('2d');
  if (rankingChart) rankingChart.destroy();
  rankingChart = new Chart(ctxRank, {
    type: 'bar',
    data: {
      labels: ['A', 'B', 'C', 'D', 'E'], // Reemplazar por partidos reales
      datasets: [{
        label: 'Delitos',
        data: [5, 10, 8, 3, 7], // Reemplazar por datos reales
        backgroundColor: [
          '#bc5090', // magenta
          '#ffa600', // naranja
          '#bc5090',
          '#ffa600',
          '#bc5090'
        ],
        borderColor: [
          '#bc5090',
          '#ffa600',
          '#bc5090',
          '#ffa600',
          '#bc5090'
        ],
        borderWidth: 1
      }]
    }
  });
}

// Integración con dashboard
function cargarKPIsYGraficos() {
  const filtros = {
    provincia: document.getElementById('provincia').value,
    partido: document.getElementById('partido').value,
    anio: document.getElementById('anio').value,
    delito: document.getElementById('delito').value
  };
  const params = new URLSearchParams(filtros);
  fetch(`/api/kpis?${params}`)
    .then(res => res.json())
    .then(kpis => {
      mostrarKPIs(kpis);
      actualizarGraficos(kpis);
    });
}

// Sobreescribe el evento del botón en dashboard.html
if (document.getElementById('btn-filtrar')) {
  document.getElementById('btn-filtrar').onclick = cargarKPIsYGraficos;
}

// Inicializa al cargar
window.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('btn-filtrar')) {
    cargarKPIsYGraficos();
  }
});

// La función mostrarKPIs debe estar definida en el template o aquí
function mostrarKPIs(kpis) {
  document.getElementById('total-delitos').textContent = kpis.total_delitos ?? '-';
  document.getElementById('total-victimas').textContent = kpis.total_victimas ?? '-';
  document.getElementById('anio-max').textContent = kpis.anio_max ?? '-';
  document.getElementById('delito-frecuente').textContent = kpis.delito_frecuente ?? '-';
  document.getElementById('promedio-delitos').textContent = kpis.promedio_delitos ?? '-';
  document.getElementById('porc-mujeres').textContent = kpis.porc_mujeres + '%' ?? '-';
  document.getElementById('porc-hombres').textContent = kpis.porc_hombres + '%' ?? '-';
  document.getElementById('tasa-delitos').textContent = kpis.tasa_delitos ?? '-';
  document.getElementById('tasa-victimas').textContent = kpis.tasa_victimas ?? '-';
}

// Rankings: actualiza tabla y gráfico de partidos
function cargarRankingPartidos() {
  const provincia = document.getElementById('provincia-rank')?.value;
  const anio = document.getElementById('anio-rank')?.value;
  const params = new URLSearchParams({ provincia, anio });
  fetch(`/api/ranking_partidos?${params}`)
    .then(res => res.json())
    .then(data => {
      // Actualiza tabla
      const tbody = document.querySelector('#tabla-ranking tbody');
      if (tbody) {
        tbody.innerHTML = '';
        data.forEach(([partido, cantidad]) => {
          const tr = document.createElement('tr');
          tr.innerHTML = `<td>${partido}</td><td>${cantidad}</td>`;
          tbody.appendChild(tr);
        });
      }
      // Actualiza gráfico
      const ctxRank = document.getElementById('rankingChart')?.getContext('2d');
      if (ctxRank) {
        if (window.rankingChart) window.rankingChart.destroy();
        window.rankingChart = new Chart(ctxRank, {
          type: 'bar',
          data: {
            labels: data.map(([partido]) => partido),
            datasets: [{
              label: 'Delitos',
              data: data.map(([_, cantidad]) => cantidad),
              backgroundColor: 'rgba(255, 99, 132, 0.2)',
              borderColor: 'rgba(255, 99, 132, 1)',
              borderWidth: 1
            }]
          }
        });
      }
    });
}
if (document.getElementById('btn-filtrar-rank')) {
  document.getElementById('btn-filtrar-rank').onclick = cargarRankingPartidos;
}

// Provincias: buscador y tabla resumen
function cargarProvincias() {
  fetch('/api/filtros')
    .then(res => res.json())
    .then(data => {
      const tbody = document.querySelector('#tabla-provincias tbody');
      if (tbody) {
        tbody.innerHTML = '';
        data.provincias.forEach(prov => {
          // Aquí podrías hacer una consulta por provincia para KPIs
          // Ejemplo: fetch(`/api/kpis?provincia=${prov}`)
          // y poblar la tabla con los resultados
          const tr = document.createElement('tr');
          tr.innerHTML = `<td>${prov}</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td>`;
          tbody.appendChild(tr);
        });
      }
    });
}
if (document.getElementById('tabla-provincias')) {
  cargarProvincias();
}

// Comparativa VS: KPIs y gráfico comparativo
function cargarComparativa() {
  const provinciaA = document.getElementById('provinciaA')?.value;
  const provinciaB = document.getElementById('provinciaB')?.value;
  if (!provinciaA || !provinciaB) return;
  Promise.all([
    fetch(`/api/kpis?provincia=${provinciaA}`).then(res => res.json()),
    fetch(`/api/kpis?provincia=${provinciaB}`).then(res => res.json())
  ]).then(([kpiA, kpiB]) => {
    // KPIs lado a lado
    document.getElementById('kpi-provA').innerHTML = `
      <ul>
        <li>Total Delitos: ${kpiA.total_delitos}</li>
        <li>Total Víctimas: ${kpiA.total_victimas}</li>
        <li>Delito más frecuente: ${kpiA.delito_frecuente}</li>
        <li>Año más crítico: ${kpiA.anio_max}</li>
        <li>% Mujeres: ${kpiA.porc_mujeres}%</li>
        <li>% Hombres: ${kpiA.porc_hombres}%</li>
        <li>Tasa Delitos: ${kpiA.tasa_delitos}</li>
        <li>Tasa Víctimas: ${kpiA.tasa_victimas}</li>
      </ul>`;
    document.getElementById('kpi-provB').innerHTML = `
      <ul>
        <li>Total Delitos: ${kpiB.total_delitos}</li>
        <li>Total Víctimas: ${kpiB.total_victimas}</li>
        <li>Delito más frecuente: ${kpiB.delito_frecuente}</li>
        <li>Año más crítico: ${kpiB.anio_max}</li>
        <li>% Mujeres: ${kpiB.porc_mujeres}%</li>
        <li>% Hombres: ${kpiB.porc_hombres}%</li>
        <li>Tasa Delitos: ${kpiB.tasa_delitos}</li>
        <li>Tasa Víctimas: ${kpiB.tasa_victimas}</li>
      </ul>`;
    // Gráfico comparativo (ejemplo: barras dobles)
    const ctxComp = document.getElementById('graficoComparativo')?.getContext('2d');
    if (ctxComp) {
      if (window.comparativaChart) window.comparativaChart.destroy();
      window.comparativaChart = new Chart(ctxComp, {
        type: 'bar',
        data: {
          labels: ['Total Delitos', 'Total Víctimas', 'Tasa Delitos', 'Tasa Víctimas'],
          datasets: [
            {
              label: provinciaA,
              data: [kpiA.total_delitos, kpiA.total_victimas, kpiA.tasa_delitos, kpiA.tasa_victimas],
              backgroundColor: 'rgba(54, 162, 235, 0.5)'
            },
            {
              label: provinciaB,
              data: [kpiB.total_delitos, kpiB.total_victimas, kpiB.tasa_delitos, kpiB.tasa_victimas],
              backgroundColor: 'rgba(255, 99, 132, 0.5)'
            }
          ]
        }
      });
    }
    // Análisis textual automático
    const analisis = [];
    if (kpiA.total_delitos > kpiB.total_delitos) {
      analisis.push(`La provincia ${provinciaA} presenta un ${(kpiA.total_delitos - kpiB.total_delitos).toFixed(0)} delitos más que ${provinciaB}.`);
    } else if (kpiB.total_delitos > kpiA.total_delitos) {
      analisis.push(`La provincia ${provinciaB} presenta un ${(kpiB.total_delitos - kpiA.total_delitos).toFixed(0)} delitos más que ${provinciaA}.`);
    }
    if (kpiA.porc_mujeres > kpiB.porc_mujeres) {
      analisis.push(`En ${provinciaA} el porcentaje de mujeres víctimas es ${(kpiA.porc_mujeres - kpiB.porc_mujeres).toFixed(1)}% mayor que en ${provinciaB}.`);
    } else if (kpiB.porc_mujeres > kpiA.porc_mujeres) {
      analisis.push(`En ${provinciaB} el porcentaje de mujeres víctimas es ${(kpiB.porc_mujeres - kpiA.porc_mujeres).toFixed(1)}% mayor que en ${provinciaA}.`);
    }
    document.getElementById('analisis-textual').textContent = analisis.join(' ');
  });
}
if (document.getElementById('btn-comparar')) {
  document.getElementById('btn-comparar').onclick = cargarComparativa;
}
