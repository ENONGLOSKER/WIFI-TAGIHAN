const yearLabels = JSON.parse(document.getElementById('year-labels').textContent);
const yearTotals = JSON.parse(document.getElementById('year-totals').textContent);

// Gunakan yearLabels dan yearTotals pada Chart.js
const revenueYearCtx = document.getElementById("revenueByYearChart").getContext("2d");
const revenueYearChart = new Chart(revenueYearCtx, {
    type: "bar",
    data: {
        labels: yearLabels,
        datasets: [{
            label: "Pendapatan (Rp)",
            data: yearTotals,
            backgroundColor: "#212529",
            borderColor: "#212529",
            borderWidth: 1,
        }],
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                beginAtZero: true,
                grid: { color: "rgba(0, 0, 0, 0.1)" },
                ticks: {
                    callback: function (value) {
                        return "Rp " + value.toLocaleString("id-ID");
                    },
                    color: "#212529",
                },
            },
            x: {
                grid: { display: false },
                ticks: { color: "#212529" },
            },
        },
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        let label = context.dataset.label || "";
                        if (label) label += ": ";
                        if (context.parsed.y !== null) {
                            label += new Intl.NumberFormat("id-ID", {
                                style: "currency",
                                currency: "IDR",
                                maximumFractionDigits: 0,
                            }).format(context.parsed.y);
                        }
                        return label;
                    },
                },
            },
        },
    },
});

// Grafik Pendapatan per Bulan (Hitam Putih)
const revenueMonthCtx = document
    .getElementById("revenueByMonthChart")
    .getContext("2d");
const revenueMonthChart = new Chart(revenueMonthCtx, {
    type: "bar",
    data: {
        labels: {{ monthly_labels| safe }},
datasets: [
    {
        label: "Pendapatan (Rp)",
        data: {{ monthly_totals| safe }},
    fill: false,
    borderColor: "#212529",
    backgroundColor: "rgba(33, 37, 41, 0.1)",
    tension: 0.1,
    pointBackgroundColor: "#212529",
    pointBorderColor: "#ffffff",
    pointBorderWidth: 2,
        },
],
    },
options: {
    responsive: true,
        maintainAspectRatio: false,
            scales: {
        y: {
            beginAtZero: true,
                grid: {
                color: "rgba(0, 0, 0, 0.1)",
          },
            ticks: {
                callback: function (value) {
                    return "Rp " + value.toLocaleString("id-ID");
                },
                color: "#212529",
          },
        },
        x: {
            grid: {
                color: "rgba(0, 0, 0, 0.1)",
          },
            ticks: {
                color: "#212529",
          },
        },
    },
    plugins: {
        legend: {
            labels: {
                color: "#212529",
          },
        },
        tooltip: {
            callbacks: {
                label: function (context) {
                    let label = context.dataset.label || "";
                    if (label) {
                        label += ": ";
                    }
                    if (context.parsed.y !== null) {
                        label += new Intl.NumberFormat("id-ID", {
                            style: "currency",
                            currency: "IDR",
                        }).format(context.parsed.y);
                    }
                    return label;
                },
            },
        },
    },
},
  });

// Grafik Pendapatan per Lokasi (Hitam Putih)
const revenueCtx = document
    .getElementById("revenueByLocationChart")
    .getContext("2d");
const revenueChart = new Chart(revenueCtx, {
    type: "bar",
    data: {
        labels: {{ lokasi_labels| safe }},
datasets: [
    {
        label: "Pendapatan (Rp)",
        data: {{ lokasi_totals| safe }},
    backgroundColor: "#212529",
    borderColor: "#212529",
    borderWidth: 1,
        },
],
    },
options: {
    responsive: true,
        maintainAspectRatio: false,
            scales: {
        y: {
            beginAtZero: true,
                grid: {
                color: "rgba(0, 0, 0, 0.1)",
          },
            ticks: {
                callback: function (value) {
                    return "Rp " + (value / 1000).toLocaleString("id-ID") + "k";
                },
                color: "#212529",
          },
        },
        x: {
            grid: {
                display: false,
          },
            ticks: {
                color: "#212529",
          },
        },
    },
    plugins: {
        legend: {
            display: false,
        },
        tooltip: {
            callbacks: {
                label: function (context) {
                    let label = context.dataset.label || "";
                    if (label) {
                        label += ": ";
                    }
                    if (context.parsed.y !== null) {
                        label += new Intl.NumberFormat("id-ID", {
                            style: "currency",
                            currency: "IDR",
                            maximumFractionDigits: 0,
                        }).format(context.parsed.y);
                    }
                    return label;
                },
            },
        },
    },
},
  });

// Grafik Status Pelanggan (Hitam Putih)
const statusCtx = document.getElementById("customerStatusChart").getContext("2d");
const statusChart = new Chart(statusCtx, {
    type: "doughnut",
    data: {
        labels: ["Aktif", "Tidak Aktif", "Suspend"],
        datasets: [
            {
                label: "Status Pelanggan",
                data: {{ status_data|safe }},
                backgroundColor: ["#000000", "#6c757d", "#212529"],
                borderColor: "#ffffff",
                borderWidth: 2,
            },
        ],
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: "#212529",
                    font: {
                        size: 12,
                    },
                },
            },
            tooltip: {
                callbacks: {
                    label: function (context) {
                        const label = context.label || "";
                        const value = context.raw || 0;
                        return `${label}: ${value} pelanggan`;
                    },
                },
            },
        },
    },
});