

var ctx = document.getElementById('temp-line-chart').getContext('2d')
var ctx2 = document.getElementById('hum-line-chart').getContext('2d')
var ctx3 = document.getElementById('ill-line-chart').getContext('2d')

var chart_data = JSON.parse(dashboardData['data']);
var weather_data = JSON.parse(weatherData['data']);

createTable(weather_data['hourly'], '#forecast-table');


var timestamps = Object.values(chart_data['iso_timestamp'])
var illuminance = Object.values(chart_data['illuminance'])
var temperature = Object.values(chart_data['temperature'])
var humidity = Object.values(chart_data['humidity'])

var illChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: timestamps,
        datasets: [{
            label: 'Temperature Trend',
            data: temperature,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 1
        }]
    },
    options: {
        fullWidth: true,
        maintainAspectRatio: false,
    }
});

var tempChart = new Chart(ctx2, {
    type: 'line',
    data: {
        labels: timestamps,
        datasets: [{
            label: 'Humidity Trend',
            data: humidity,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 1
        }]
    },
    options: {
        fullWidth: true,
        maintainAspectRatio: false,
    }
});

var humChart = new Chart(ctx3, {
    type: 'line',
    data: {
        labels: timestamps,
        datasets: [{
            label: 'Illuminance Trend',
            data: illuminance,
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 1
        }]
    },
    options: {
        fullWidth: true,
        maintainAspectRatio: false,
    }
});

function createTable(data, selector){
    console.log(data)
    var wanted_cols = ['dt', 'temp','pressure','humidity', 'clouds','wind_speed']
    var columns =  Object.keys(data[0]);
    var htmlTable = '<table class="table table-sm">';
    htmlTable += '<thead class="thead-dark"><tr>';
    for(k = 0; k<columns.length; k++){ 
        if(wanted_cols.includes(columns[k])) {
            htmlTable += `<td>${columns[k]}</td>`;
        }
    }
    htmlTable += '</tr></thead><tbody>';
    for(let i = 0; i<data.length;i++){
        htmlTable += `<tr>`;
        for(j = 0; j<columns.length; j++){
            if(wanted_cols.includes(columns[j])) {
                if(columns[j] == 'dt'){
                    console.log(data[i][columns[j]])
                    var ts = new Date(data[i][columns[j]] * 1000).toISOString().substr(0,16).replace('T', ' ');
                    htmlTable += `<td>${ts}</td>`;
                } else {
                    htmlTable += `<td>${data[i][columns[j]]}</td>`;
                }
            }
            
        }
        htmlTable += `</tr>`
    }
    htmlTable += '</tbody></table>';
    $(selector).html(htmlTable)
}