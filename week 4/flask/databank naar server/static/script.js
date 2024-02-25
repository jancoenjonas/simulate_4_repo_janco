
    function toggleNavMenu() {
        var navMenu = document.getElementById("nav-menu");
        navMenu.classList.toggle("show");
        var navItems = document.querySelectorAll(".nav-item");
        navItems.forEach(function(item) {
            item.classList.toggle("show");
        });
    }


        function toggleNavMenu() {
            var navMenu = document.getElementById("nav-menu");
            navMenu.classList.toggle("show");
            var navItems = document.querySelectorAll(".nav-item");
            navItems.forEach(function(item) {
                item.classList.toggle("show");
            });
        }

        function updateAttendance(studentId, lessonId, newStatus) {
            console.log("Student ID:", studentId, "Lesson ID:", lessonId, "New Status:", newStatus);

            fetch('/update_attendance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ studentId: studentId, lessonId: lessonId, newStatus: newStatus })
            })

            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok ' + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                console.log('Success:', data);
                alert('Attendance updated successfully!'); // Alert for debugging
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('Error updating attendance!'); // Alert for debugging
            });
        }
