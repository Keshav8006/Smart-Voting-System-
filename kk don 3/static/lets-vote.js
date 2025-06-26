

document.addEventListener('DOMContentLoaded', function () {
    const colorDropdown = document.getElementById('color');
    const voteButton = document.getElementById('voteButton');
    const clearButton = document.getElementById('clearButton');
    const pieChartButton = document.getElementById('pieChartButton');
    const resultMessage = document.getElementById('result');
    const votesList = document.getElementById('votesList');
    let myChart;

    voteButton.addEventListener('click', function () {
        const selectedColor = colorDropdown.value;
        let colorVotes = JSON.parse(localStorage.getItem('colorVotes')) || {};
        colorVotes[selectedColor] = (colorVotes[selectedColor] || 0) + 1;
        localStorage.setItem('colorVotes', JSON.stringify(colorVotes));
        resultMessage.textContent =` You voted for ${selectedColor}.`;
        displayVotes();
    });

    clearButton.addEventListener('click', function () {
        localStorage.removeItem('colorVotes');
        resultMessage.textContent = 'All votes cleared.';
        displayVotes();
        if (myChart) {
            myChart.destroy();
        }
    });

    pieChartButton.addEventListener('click', function () {
        const colorVotes = JSON.parse(localStorage.getItem('colorVotes')) || {};
        const colors = Object.keys(colorVotes);
        const votes = Object.values(colorVotes);

        if (myChart) {
            myChart.destroy();
        }

        const ctx = document.getElementById('pieChart').getContext('2d');
        myChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: colors,
                datasets: [{
                    label: 'Votes',
                    data: votes,
                    backgroundColor: [
                        'rgb(255, 99, 132)',
                        'rgb(54, 162, 235)',
                        'rgb(255, 205, 86)',
                        'rgb(75, 192, 192)',
                    ],
                    hoverOffset: 4
                }]
            },
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: 'Voting Results'
                    }
                }
            }
        });
    });

    function displayVotes() {
        votesList.innerHTML = '';
        const colorVotes = JSON.parse(localStorage.getItem('colorVotes')) || {};
        for (const color in colorVotes) {
            const listItem = document.createElement('li');
            listItem.textContent = `${color}: ${colorVotes[color]} votes`;
            votesList.appendChild(listItem);
        }
    }

    displayVotes();
});