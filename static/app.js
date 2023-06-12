document.addEventListener('DOMContentLoaded', function() {
    // Retrieve the passed data from Flask and parse it
    var data = JSON.parse('{{ data | safe }}');

    // Extract the necessary values for the chart
    var labels = data.map(entry => entry.start_date);
    var values = data.map(entry => entry.average_per_hour);

    // Calculate the cumulative values
    var cumulativeValues = [];
    var cumulativeSum = 0;
    for (var i = 0; i < values.length; i++) {
        cumulativeSum += values[i];
        cumulativeValues.push(cumulativeSum);
    }

    // Create the chart using Chart.js
    var ctx = document.getElementById('myChart').getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cumulative Production per Hour',
                data: cumulativeValues,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
