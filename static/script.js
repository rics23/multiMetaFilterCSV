function toggleField(field) {
    var checkBox = document.getElementById('check_' + field);
    var fieldDiv = document.getElementById('field_' + field);
    if (checkBox.checked) {
        fieldDiv.style.display = '';
    } else {
        fieldDiv.style.display = 'none';
    }
    // Save the field selection whenever a checkbox is toggled
    saveFieldSelection();
}

function saveFieldSelection() {
    var checkboxes = document.querySelectorAll('input[type=checkbox]');
    var selectedFields = [];
    checkboxes.forEach(function(checkbox) {
        if (checkbox.checked) {
            selectedFields.push(checkbox.id.replace('check_', ''));
        }
    });

    fetch('/save_selected_fields', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(selectedFields),
    })
    .then(response => response.json())
    .then(data => console.log(data.message))
    .catch(error => console.error('Error:', error));
}

function loadFieldSelection() {
    var selectedFields = JSON.parse(document.getElementById('selectedFieldsData').textContent);
    var checkboxes = document.querySelectorAll('input[type=checkbox]');
    checkboxes.forEach(function(checkbox) {
        var field = checkbox.id.replace('check_', '');
        if (selectedFields.includes(field)) {
            checkbox.checked = true;
            document.getElementById('field_' + field).style.display = '';
        } else {
            checkbox.checked = false;
            document.getElementById('field_' + field).style.display = 'none';
        }
    });
}

document.addEventListener('DOMContentLoaded', loadFieldSelection);
window.onbeforeunload = saveFieldSelection;
