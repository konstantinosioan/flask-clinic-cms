function confirmDeletion() {
    let forms = document.querySelectorAll('.confirm-delete');

    for (const form of forms) {
        form.addEventListener('submit', function(event) {
            if (!confirm('Θέλετε σίγουρα να διαγράψετε αυτό το στοιχείο;')) {
                event.preventDefault();
            }
        });
    }
}

confirmDeletion();