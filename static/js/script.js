let uploadedFilename = '';
let downloadURL = '';

function uploadPDF() {
    const fileInput = document.getElementById('pdfFile');
    const file = fileInput.files[0];
    if (!file) return alert('Please select a PDF file.');

    const formData = new FormData();
    formData.append('pdf', file);

    document.getElementById('status').innerText = 'Uploading...';

    fetch('/upload', { method: 'POST', body: formData })
        .then(response => response.json())
        .then(data => {
            uploadedFilename = data.filename;
            document.getElementById('convertBtn').style.display = 'inline';
            document.getElementById('status').innerText = 'File uploaded. Ready to convert.';
        }).catch(error => {
            console.error(error);
            document.getElementById('status').innerText = 'Upload failed.';
        });
}

function convertPDF() {
    document.getElementById('status').innerText = 'Converting...';

    fetch('/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: uploadedFilename })
    })
    .then(response => response.json())
    .then(data => {
        downloadURL = data.download_url;
        document.getElementById('downloadBtn').style.display = 'inline';
        document.getElementById('status').innerText = 'Conversion complete. Ready to download.';
    }).catch(error => {
        console.error(error);
        document.getElementById('status').innerText = 'Conversion failed.';
    });
}

function downloadFile() {
    window.location.href = downloadURL;
}
