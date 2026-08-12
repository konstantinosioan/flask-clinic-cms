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


function revealOnScroll() {
    const targets = document.querySelectorAll('.js-reveal');

    const observer = new IntersectionObserver((entries) => {
        for (const entry of entries) {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        }
    }, { threshold: 0.1 });

    for (const target of targets) {
        target.classList.add('reveal');
        observer.observe(target);
    }
}

revealOnScroll();


function setupAnnouncementsToggle() {
    const items = document.querySelectorAll('.announcement-item');
    const visibleCount = 3;
    const button = document.getElementById('show-more-announcements');

    if (items.length <= visibleCount) {
        return;
    }

    const hiddenItems = Array.from(items).slice(visibleCount);

    for (const item of hiddenItems) {
        item.classList.add('d-none');
    }

    button.classList.remove('d-none');
    button.addEventListener('click', () => {
        for (const item of hiddenItems) {
            item.classList.remove('d-none');
        }

        button.classList.add('d-none');
    });
}

setupAnnouncementsToggle();


function closeNavbarOnLinkClick() {
    const navbarCollapseEl = document.getElementById('navbarNav');
    const navLinks = navbarCollapseEl.querySelectorAll('.nav-link');

    for (const link of navLinks) {
        link.addEventListener('click', (event) => {
            const isMenuOpen = navbarCollapseEl.classList.contains('show');
            const targetSection = link.hash ? document.querySelector(link.hash) : null;

            // On mobile the menu-close animation shifts the page layout, so scrolling
            // has to wait until it fully finishes, or the target position lands wrong
            if (isMenuOpen && targetSection) {
                event.preventDefault();
                navbarCollapseEl.addEventListener('hidden.bs.collapse', () => {
                    targetSection.scrollIntoView({ behavior: 'smooth' });
                }, { once: true });
            }

            bootstrap.Collapse.getOrCreateInstance(navbarCollapseEl).hide();
        });
    }
}

closeNavbarOnLinkClick();
