// A tool for streamlining systematic literature reviews, combining CSV
// projects from diverse databases, standardising results on a local web page
// for efficient duplicate detection, inclusion/exclusion tracking, and
// PRISMA-aligned visualisations and supporting files.
// Copyright (C) 2024  Ricardo Lopes  rics.23@gmail.com

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

async function handleAction(event, action, recordId) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    if (action === 'exclude') {
        const exclusionReason = form.querySelector('select[name="exclusion_reason"]').value;
        formData.append('inclusion_importance', '');
        formData.append('exclusion_reason', exclusionReason);
    }

    if (action === 'include') {
        const inclusionImportance = form.querySelector('select[name="inclusion_importance"]').value;
        formData.append('inclusion_importance', inclusionImportance);
        formData.append('exclusion_reason', '');
    }

    try {
        const response = await fetch(`/action/${action}/${recordId}`, {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        console.log(result); // Log the entire result object
        if (result.status === 'success') {
            updateRecord(result.record, result.record_id, result.total_records, result.included_count, result.excluded_count, result.duplicates_count);
        } else {
            console.error(result.message);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function updateRecord(record, recordId, totalRecords, includedCount, excludedCount, duplicatesCount) {
    console.log(`Updating record with ID: ${recordId}`);
    console.log(`Total Records: ${totalRecords}, Included: ${includedCount}, Excluded: ${excludedCount}, Duplicates: ${duplicatesCount}`);

    if (recordId === -1) {
        document.querySelector('.record-details').innerHTML = "<p>No more records.</p>";
        return;
    }

    const recordDetails = document.querySelector('.record-details ul');
    recordDetails.innerHTML = '';

    for (const [key, value] of Object.entries(record)) {
        const li = document.createElement('li');
        li.id = `field_${key}`;
        li.innerHTML = `<strong>${key}:</strong> ${value}`;
        recordDetails.appendChild(li);
    }

    // Update the status bar with the new counts
    document.querySelector('.total-records').innerText = `Records: ${totalRecords}`;
    document.querySelector('.included-count').innerText = `Included: ${includedCount}`;
    document.querySelector('.excluded-count').innerText = `Excluded: ${excludedCount}`;
    document.querySelector('.duplicates-count').innerText = `Duplicates: ${duplicatesCount}`;
}

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
