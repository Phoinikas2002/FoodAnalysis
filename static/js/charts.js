document.addEventListener('DOMContentLoaded', function() {
    // 评论数量分析图表
    var ctx1 = document.getElementById('reviewChart').getContext('2d');
    var reviewChart = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: ['商家A', '商家B', '商家C'], // 替换为实际数据
            datasets: [{
                label: '评论数量',
                data: [100, 200, 300], // 替换为实际数据
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

    // 消费水平分析图表
    var ctx2 = document.getElementById('spendingChart').getContext('2d');
    var spendingChart = new Chart(ctx2, {
        type: 'line',
        data: {
            labels: ['商家A', '商家B', '商家C'], // 替换为实际数据
            datasets: [{
                label: '人均消费',
                data: [50, 60, 70], // 替换为实际数据
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                borderColor: 'rgba(153, 102, 255, 1)',
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

    // 评分分析图表
    var ctx3 = document.getElementById('ratingChart').getContext('2d');
    var ratingChart = new Chart(ctx3, {
        type: 'pie',
        data: {
            labels: ['口味', '环境', '服务'], // 替换为实际数据
            datasets: [{
                label: '评分',
                data: [4.5, 4.0, 3.5], // 替换为实际数据
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)'
                ],
                borderWidth: 1
            }]
        }
    });
});
