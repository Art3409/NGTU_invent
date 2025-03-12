document.addEventListener('DOMContentLoaded', function () {
    const table = document.getElementById('itemsTable');
     if (table) {
    const inputFields = table.querySelectorAll('thead .search-row .search-input');
    inputFields.forEach((input, index) => {
        input.addEventListener('keyup', function () {
            filterTable(index);
        });
    });
        function filterTable(columnIndex) {
            const filterValue = inputFields[columnIndex].value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');

            rows.forEach(row => {
                const cell = row.querySelectorAll('td')[columnIndex];
                if (cell) {
                    let cellText = "";
                    if (columnIndex === 4) {
                        if (cell.textContent.trim() === 'Не присвоено') {
                            cellText = 'Не присвоено'.toLowerCase();
                        } else {
                            cellText = cell.textContent.toLowerCase();
                        }
                    } else {
                        cellText = cell.textContent.toLowerCase();
                    }
                    if (cellText.includes(filterValue)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                }
            });
        }
    }
});