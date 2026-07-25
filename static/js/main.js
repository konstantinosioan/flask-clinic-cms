function confirmDeletion() {
    const forms = document.querySelectorAll('.confirm-delete');

    for (const form of forms) {
        form.addEventListener('submit', (event) => {
            if (!confirm('Θέλετε σίγουρα να διαγράψετε αυτό το στοιχείο;')) {
                event.preventDefault();
            }
        });
    }
}

confirmDeletion();


function showPreview() {
    const fileInputs = document.querySelectorAll('.photo-input');

    for (const fileInput of fileInputs) {
        fileInput.addEventListener('change', () => {
            const file = fileInput.files[0];
            const preview = document.getElementById(fileInput.id + '-preview');
            const reader = new FileReader();

            reader.addEventListener('load', () => {
                preview.src = reader.result;
                preview.classList.remove('d-none');
            });

            if (file) {
                reader.readAsDataURL(file);
            }
        });
    }
}

showPreview();
