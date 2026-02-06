// Função para atualizar tema dos gráficos sem recarregar
function updateChartsTheme() {
    const isDark = document.documentElement.classList.contains('dark');
    
    // Atualiza gráfico de evolução
    if (typeof chartInstance !== 'undefined' && chartInstance) {
        chartInstance.options.scales.y.ticks.color = isDark ? '#D1D5DB' : '#6B7280';
        chartInstance.options.scales.x.ticks.color = isDark ? '#D1D5DB' : '#6B7280';
        chartInstance.options.scales.y.grid.color = isDark ? 'rgba(75, 85, 99, 0.3)' : 'rgba(0,0,0,0.05)';
        chartInstance.options.plugins.legend.labels.color = isDark ? '#D1D5DB' : '#374151';
        chartInstance.options.plugins.tooltip.backgroundColor = isDark ? '#1F2937' : '#FFFFFF';
        chartInstance.options.plugins.tooltip.titleColor = isDark ? '#F9FAFB' : '#111827';
        chartInstance.options.plugins.tooltip.bodyColor = isDark ? '#D1D5DB' : '#374151';
        chartInstance.options.plugins.tooltip.borderColor = isDark ? '#374151' : '#E5E7EB';
        chartInstance.update();
    }
    
    // Atualiza gráfico pizza
    if (typeof pizzaChart !== 'undefined' && pizzaChart) {
        pizzaChart.data.datasets[0].backgroundColor = isDark ? 
            ['#60A5FA', '#FBBF24', '#34D399', '#F87171', '#A78BFA', '#F472B6', '#2DD4BF', '#FB923C'] :
            ['#3B82F6', '#FBBF24', '#10B981', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'];
        pizzaChart.data.datasets[0].borderColor = isDark ? '#1F2937' : '#fff';
        pizzaChart.options.plugins.legend.labels.color = isDark ? '#D1D5DB' : '#374151';
        pizzaChart.options.plugins.tooltip.backgroundColor = isDark ? '#1F2937' : '#FFFFFF';
        pizzaChart.options.plugins.tooltip.titleColor = isDark ? '#F9FAFB' : '#111827';
        pizzaChart.options.plugins.tooltip.bodyColor = isDark ? '#D1D5DB' : '#374151';
        pizzaChart.options.plugins.tooltip.borderColor = isDark ? '#374151' : '#E5E7EB';
        pizzaChart.update();
    }
}