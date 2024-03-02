
    function toggleNavMenu() {
        var navMenu = document.getElementById("nav-menu");
        navMenu.classList.toggle("show");
        var navItems = document.querySelectorAll(".nav-item");
        navItems.forEach(function(item) {
            item.classList.toggle("show");
        });
    }

