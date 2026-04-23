// --- CLOCK ---
function updateClock() {
    const now = new Date();
    const date = now.toLocaleDateString('en-GB');
    const time = now.toLocaleTimeString();
    document.getElementById('current-date').textContent = `Date: ${date}`;
    document.getElementById('current-time').textContent = `Time: ${time}`;
}

// --- ALARM ---
function turnAlarmOff() {
    fetch('/alarm/off')
        .then(() => alert('Alarm turned OFF'))
        .catch(err => console.error(err));
    document.getElementById('alarmOffButton').style.backgroundColor = '#d32f2f';
}

// --- DROPDOWN FILTER ---
function toggleDropdown() {
    document.getElementById('filterDropdown').classList.toggle('show');
}

// --- DURATION FILTER BUTTONS ---
function setDurationFilter(min, max) {
    document.getElementById('minDuration').value = min;
    document.getElementById('maxDuration').value = max;
    applyFilters();
}

// --- APPLY FILTERS ---
async function applyFilters() {
    const params = new URLSearchParams();
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const minDuration = document.getElementById('minDuration').value;
    const maxDuration = document.getElementById('maxDuration').value;
    const minId = document.getElementById('minId').value;
    const maxId = document.getElementById('maxId').value;

    if(startDate) params.append('start_date', startDate);
    if(endDate) params.append('end_date', endDate);
    if(minDuration) params.append('min_duration', minDuration);
    if(maxDuration) params.append('max_duration', maxDuration);
    if(minId) params.append('min_id', minId);
    if(maxId) params.append('max_id', maxId);

    await loadEvents(params);
}

// --- LOAD EVENTS ---
async function loadEvents(params='') {
    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');
    const table = document.getElementById('eventsTable');
    const tbody = document.getElementById('tableBody');

    loadingState.style.display = 'block';
    table.style.display = 'none';
    emptyState.style.display = 'none';
    tbody.innerHTML = '';

    try {
        const response = await fetch(`/api/events?${params}`);
        const data = await response.json();
        loadingState.style.display = 'none';

        if(!data.events || data.events.length === 0){
            emptyState.style.display = 'block';
            return;
        }

        data.events.forEach(event => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${event['crushing_id'] || '-'}</td>
                <td>${event['date'] || '-'}</td>
                <td>${event['event_timestamp'] || '-'}</td>
                <td>${event['crushing_duration'] || '-'}</td>
                <td class="${event['alarm']==='Activated'?'status-activated':'status-inactive'}">${event['alarm'] || '-'}</td>
                <td>${event['alarm_timestamp'] || '-'}</td>
                <td><button class="download-btn" onclick="viewMedia('${event['image_path'] || '#'}')">🖼️ View</button></td>
                <td><button class="download-btn" onclick="viewMedia('${event['video_path'] || '#'}')">🎥 View</button></td>
            `;
            tbody.appendChild(row);
        });

        table.style.display = 'table';
    } catch(err){
        console.error(err);
        loadingState.textContent = 'Error loading events';
    }
}

// --- VIEW MEDIA MODAL ---
function viewMedia(path) {
    if(!path || path === '#'){ 
        alert('No media available'); 
        return; 
    }

    // Remove old modal if exists
    const oldModal = document.getElementById('mediaModal');
    if(oldModal) oldModal.remove();

    const modal = document.createElement('div');
    modal.id = 'mediaModal';
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.8); display: flex; justify-content: center;
        align-items: center; z-index: 1000;
    `;

    const ext = path.split('.').pop().toLowerCase();
    let media;

    if(['mp4','webm','ogg'].includes(ext)){
        media = document.createElement('video');
        media.src = `/static/${path}`; // ✅ Correct path to static folder
        media.controls = true;
        media.autoplay = true;
        media.style.maxWidth = '90%';
        media.style.maxHeight = '80%';
        // prevent clicks on the video from closing the modal
        media.addEventListener('click', e => e.stopPropagation());
    } else {
        media = document.createElement('img');
        media.src = `/static/${path}`; // ✅ Correct path to static folder
        media.style.maxWidth = '90%';
        media.style.maxHeight = '80%';
        media.style.borderRadius = '8px';
        // prevent clicks on the image from closing the modal
        media.addEventListener('click', e => e.stopPropagation());
    }

    modal.appendChild(media);
    // only close when clicking the backdrop (modal itself), not the media
    modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
    document.body.appendChild(modal);
}

// --- RESET FILTERS ---
function resetFilters() {
    document.getElementById('startDate').value = '';
    document.getElementById('endDate').value = '';
    document.getElementById('minDuration').value = '';
    document.getElementById('maxDuration').value = '';
    document.getElementById('minId').value = '';
    document.getElementById('maxId').value = '';
    document.querySelectorAll('.quick-filter-btn').forEach(btn => btn.classList.remove('active'));
    applyFilters();
}

// --- EXPORT CSV ---
function exportCSV() {
    const params = new URLSearchParams();
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const minDuration = document.getElementById('minDuration').value;
    const maxDuration = document.getElementById('maxDuration').value;
    const minId = document.getElementById('minId').value;
    const maxId = document.getElementById('maxId').value;

    if(startDate) params.append('start_date', startDate);
    if(endDate) params.append('end_date', endDate);
    if(minDuration) params.append('min_duration', minDuration);
    if(maxDuration) params.append('max_duration', maxDuration);
    if(minId) params.append('min_id', minId);
    if(maxId) params.append('max_id', maxId);

    window.location.href = `/api/export-csv?${params}`;
}

// --- INIT ---
updateClock();
setInterval(updateClock, 1000);
loadEvents();