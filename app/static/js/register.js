function showLoader() {
    $("#loader").show();
}

function hideLoader() {
    $("#loader").hide();
}

$(document).ready(function () {
    const fields = [
        { id: "#FirstName", name: "First Name" },
        { id: "#LastName", name: "Last Name" },
        { id: "#username", name: "User Name" },
        { id: "#password", name: "Password" },
        { id: "#phone_number", name: "Phone Number" },
        { id: "#email", name: "Email" },
        { id: "#address", name: "Address" },
        { id: "#state", name: "State" },
        { id: "#district", name: "District" },
        { id: "#date_of_birth", name: "Date of Birth" },
    ];

    $("#registerForm").on("submit", function (e) {
        e.preventDefault();

        $(".error").text(""); // Clear previous errors
        $("#formMessage").text("").removeClass("success error");
        let valid = true;

        // Validate required fields
        fields.forEach(function (field) {
            const el = $(field.id);
            if (el.length === 0) {
                console.warn(`Field element ${field.id} not found`);
                return;
            }
            const value = el.val().trim();
            if (!value) {
                el.siblings(".error").text(field.name + " is required.");
                valid = false;
            }
        });

        if (!valid) return;

        const formData = new FormData(this);

        // Show loader before AJAX starts
        showLoader();

        $.ajax({
            url: "/app/register/",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function (response) {
                if (response.success) {
                    $("#formMessage").text(response.message).addClass("success");
                    $("#registerForm")[0].reset();
                    $("#district").empty().append('<option value="">-- Select District --</option>');
                } else {
                    $("#formMessage").text(response.message || response.error).addClass("error");
                }
            },
            error: function (xhr, status, error) {
                $("#formMessage").text("An error occurred while saving the user.").addClass("error");
                console.error("AJAX error:", error);
            },
            complete: function () {
                // Hide loader after AJAX finishes (success or error)
                hideLoader();
            }
        });
    });

    $("#state").on("change", function () {
        const stateId = $(this).val();
        if (stateId) {
            $.ajax({
                url: "/app/get-districts/",
                type: "GET",
                data: { state_id: stateId },
                success: function (data) {
                    $("#district").empty().append('<option value="">-- Select District --</option>');
                    $.each(data, function (index, district) {
                        $("#district").append('<option value="' + district.id + '">' + district.name + '</option>');
                    });
                },
                error: function () {
                    console.error("Failed to fetch districts.");
                },
                complete: hideLoader
            });
        } else {
            $("#district").empty().append('<option value="">-- Select District --</option>');
        }
    });
});
