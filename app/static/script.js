document.addEventListener("DOMContentLoaded", function () {
  // auto fill ngày hôm nay cho input.auto-today (nếu rỗng)
  const dateInputs = document.querySelectorAll("input.auto-today[type='date']");
  if (dateInputs.length) {
    const t = new Date();
    const y = t.getFullYear();
    const m = ("0" + (t.getMonth() + 1)).slice(-2);
    const d = ("0" + t.getDate()).slice(-2);
    const today = `${y}-${m}-${d}`;
    dateInputs.forEach(i => { if (!i.value) i.value = today; });
  }

  initDashboardChart();
});

// Biểu đồ thu/chi trên dashboard
function initDashboardChart() {
  if (typeof Chart === "undefined") return;

  const incomeEl = document.getElementById("dashIncome");
  const expenseEl = document.getElementById("dashExpense");
  const canvas = document.getElementById("dashboardChart");

  if (!incomeEl || !expenseEl || !canvas) return;

  const income = parseFloat(incomeEl.dataset.value || "0");
  const expense = parseFloat(expenseEl.dataset.value || "0");

  if (income === 0 && expense === 0) return;

  new Chart(canvas.getContext("2d"), {
    type: "pie",
    data: {
      labels: ["Thu", "Chi"],
      datasets: [{
        data: [income, expense],
        backgroundColor: ["#16a34a", "#ef4444"],
        borderWidth: 0
      }]
    },
    options: {
      plugins: { legend: { position: "bottom" } }
    }
  });
}
