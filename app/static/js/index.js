// Global loading handlers
let isLoading = false;

// Function to show/hide spinner
// Updated spinner control function
function toggleSpinner(show, message = "Loading...") {
  if (show) {
    isLoading = true;
    $("#spinner .spinner-text").text(message);
    $("#spinner").addClass("show").removeClass("hide");
  } else {
    isLoading = false;
    $("#spinner").removeClass("show").addClass("hide");
  }
}
// Function to display messages
function displayMessage(msg, type) {
  const alertClass =
    type === "danger"
      ? "alert-danger"
      : type === "warning"
      ? "alert-warning"
      : "alert-success";
  $("#formMessage")
    .removeClass("d-none")
    .addClass("alert " + alertClass + " d-block")
    .html(msg);
}

// Login form initialization
function initLoginForm() {
  $.ajaxSetup({
    headers: {
      "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val(),
    },
  });

  $("#loginInfo")
    .off("submit")
    .on("submit", function (e) {
      e.preventDefault();
      e.stopPropagation();

      $(".error").text("");
      $("#formMessage")
        .removeClass("alert-success alert-danger d-block")
        .addClass("d-none")
        .html("");

      let valid = true;
      const username = $("#name").val().trim();
      const password = $("#password").val().trim();
      const captcha = $("#captcha").val().trim();

      if (!username) {
        $("#name").siblings(".error").text("Username is required.");
        valid = false;
      }
      if (!password) {
        $("#password").siblings(".error").text("Password is required.");
        valid = false;
      }
      if (!captcha) {
        $("#captcha").siblings(".error").text("Captcha is required.");
        valid = false;
      }
      if (!valid) return false;

      toggleSpinner(true, "Signing you in...");

      $.ajax({
        url: $("#loginInfo").attr("action"),
        type: "POST",
        data: $(this).serialize(),
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
        success: function (response) {
          if (response.success && response.html) {
            $("#main-content").html(response.html);
            history.pushState({}, "", response.redirect_url);
            new WOW().init();

            // Update navbar after login success
            updateNavbar();
          } else if (response.message) {
            displayMessage(response.message, "danger");
            if (response.captcha) {
              $("#captchaImage").html(response.captcha);
            }
          } else {
            displayMessage("Unexpected response from server.", "danger");
          }
        },
        error: function () {
          displayMessage("Something went wrong. Try again.", "danger");
        },
        complete: function() {
          toggleSpinner(false);
        }
      });

      return false;
    });

  // Captcha refresh button handler
  $("#refreshCaptchaBtn")
    .off("click")
    .on("click", function () {
      $(this).prop("disabled", true);
      toggleSpinner(true,"refresh Captcha ...");

      $.ajax({
        url: refreshCaptchaUrl,
        type: "GET",
        success: function (data) {
          if (data.captcha) {
            $("#captchaImage").html(data.captcha);
            $("#captcha").val("");
          }
        },
        error: function (xhr, status, error) {
          console.error("Captcha refresh error:", error);
          displayMessage("Failed to refresh captcha", "danger");
        },
        complete: function () {
          $("#refreshCaptchaBtn").prop("disabled", false);
          toggleSpinner(false);
        },
      });
    });
}

// Registration form initialization
function initRegisterForm() {
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

  $("#registerForm")
    .off("submit")
    .on("submit", function (e) {
      e.preventDefault();
      e.stopPropagation();

      $(".error").text("");
      $("#formMessage")
        .removeClass("alert-success alert-danger d-block")
        .addClass("d-none")
        .html("");

      let valid = true;
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

      if (!valid) return false;

      toggleSpinner(true, "Creating your account...");
      const formData = new FormData(this);

      $.ajax({
        url: $(this).attr("action"),
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
        success: function (response) {
          if (response.success) {
            displayMessage(response.message, "success");
            $("#registerForm")[0].reset();
            $("#district")
              .empty()
              .append('<option value="">-- Select District --</option>');

            // Redirect to login page after successful registration
            if (response.redirect_url) {
              setTimeout(() => {
                loadPage(response.redirect_url);
              }, 2000);
            }
          } else {
            displayMessage(response.message || response.error, "danger");
            if (response.errors) {
              // Handle field-specific errors if returned by server
              Object.keys(response.errors).forEach((field) => {
                $(`#${field}`).siblings(".error").text(response.errors[field]);
              });
            }
          }
        },
        error: function (xhr, status, error) {
          displayMessage("An error occurred while saving the user.", "danger");
          console.error("Registration error:", error);
        },
        complete: function() {
          toggleSpinner(false);
        }
      });

      return false;
    });

  // State change handler for districts
  $("#state")
    .off("change")
    .on("change", function () {
      const stateId = $(this).val();
      if (stateId) {
        toggleSpinner(true,'Loading districts...');
        $.ajax({
          url: "/app/get-districts/",
          type: "GET",
          data: { state_id: stateId },
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
          success: function (data) {
            $("#district")
              .empty()
              .append('<option value="">-- Select District --</option>');
            $.each(data, function (index, district) {
              $("#district").append(
                '<option value="' +
                  district.id +
                  '">' +
                  district.name +
                  "</option>"
              );
            });
          },
          error: function () {
            console.error("Failed to fetch districts.");
          },
          complete: function() {
            toggleSpinner(false);
          }
        });
      } else {
        $("#district")
          .empty()
          .append('<option value="">-- Select District --</option>');
      }
    });
}

// AJAX page loading function
function loadPage(url) {
  toggleSpinner(true, "Loading page...");
  $.ajax({
    url: url,
    headers: { "X-Requested-With": "XMLHttpRequest" },
    success: function (data) {
      var htmlContent = data.html || data;
      var tempDiv = $("<div>").html(htmlContent);
      var newContent = tempDiv.find("#main-content").html();

      if (newContent) {
        $("#main-content").html(newContent);
      } else {
        $("#main-content").html(htmlContent);
      }

      new WOW().init();

      if (url.includes("/login")) {
        initLoginForm();
      } else if (url.includes("/register")) {
        initRegisterForm();
      } else if (url.includes("/update_profile")) {
        initUpdateProfileForm();
      }
    },
    error: function () {
      displayMessage("Failed to load page.", "danger");
    },
    complete: function() {
      toggleSpinner(false);
    }
  });
}

// Update navbar dynamically (used after login/logout)
function updateNavbar() {
  toggleSpinner(true,'update navbar...');
  $.ajax({
    url: "/app/navbar/",
    headers: { "X-Requested-With": "XMLHttpRequest" },
    success: function (response) {
      $(".container-fluid.bg-white.sticky-top").replaceWith(
        $(response.html).filter(".container-fluid.bg-white.sticky-top")
      );
    },
    error: function () {
      console.error("Failed to update navbar.");
    },
    complete: function() {
      toggleSpinner(false);
    }
  });
}

// Document ready handler
$(document).ready(function () {
  new WOW().init();

  if (window.location.pathname.includes("/login")) {
    initLoginForm();
  } else if (window.location.pathname.includes("/register")) {
    initRegisterForm();
  }

  // Handle navbar link clicks with AJAX load
  $(document).on(
    "click",
    ".navbar-nav a#nav-item.nav-link, .navbar-nav .dropdown-menu a.dropdown-item",
    function (e) {
      e.preventDefault();

      var url = $(this).attr("href");
      if (url === window.location.pathname) {
        return;
      }

      loadPage(url);
    }
  );

  // Handle back/forward buttons
  window.onpopstate = function () {
    loadPage(location.pathname);
  };
});

// CSRF token getter from cookie
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");
$.ajaxSetup({
  headers: { "X-CSRFToken": csrftoken },
});
$.ajaxSetup({
  beforeSend: function (xhr, settings) {
    if (
      !/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) &&
      !this.crossDomain
    ) {
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  },
});

// Logout handler with CSRF token in data
$(document).on("click", "#logoutBtn", function (e) {
  e.preventDefault();
  toggleSpinner(true, "Logging out...");
  $.ajax({
    type: "POST",
    url: "/app/logout/",
    data: { csrfmiddlewaretoken: csrftoken },
    headers: { "X-Requested-With": "XMLHttpRequest" },
    success: function (response) {
      if (response.success) {
        console.log(response.message);
        loadPage("/app/"); // SPA reload home
        updateNavbar(); // Update navbar for guest (logged out)
      } else {
        alert("Logout failed.");
      }
    },
    error: function (xhr) {
      console.error("Logout error:", xhr.responseText);
      alert("Error: Could not logout. CSRF missing?");
    },
    complete: function() {
      toggleSpinner(false);
    }
  });
});

function initUpdateProfileForm() {
  console.log("1");
  $("#state")
    .off("change")
    .on("change", function () {
      const stateId = $(this).val();
      if (stateId) {
        toggleSpinner(true, "Loading districts...");
        $.ajax({
          url: "/app/get-districts/",
          type: "GET",
          data: { state_id: stateId },
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
          success: function (data) {
            $("#district")
              .empty()
              .append('<option value="">-- Select District --</option>');
            $.each(data, function (index, district) {
              $("#district").append(
                '<option value="' +
                  district.id +
                  '">' +
                  district.name +
                  "</option>"
              );
            });
          },
          error: function () {
            console.error("Failed to fetch districts.");
          },
          complete: function() {
            toggleSpinner(false);
          }
        });
      } else {
        $("#district")
          .empty()
          .append('<option value="">-- Select District --</option>');
      }
    });

  $("#updateProfileForm")
    .off("submit")
    .on("submit", function (e) {
      e.preventDefault();
      console.log("2");

      $(".error").text("");
      $("#ajaxResponseMessage").html("");

      let valid = true;
      console.log("3");
      // Validate First Name
      let firstName = $("#first_name").val().trim();
      if (firstName === "") {
        $("#first_name").siblings(".error").text("First Name is required.");
        valid = false;
      } else if (!/^[a-zA-Z\s]+$/.test(firstName)) {
        $("#first_name")
          .siblings(".error")
          .text("First Name can only contain letters.");
        valid = false;
      }

      // Validate Last Name
      let lastName = $("#last_name").val().trim();
      if (lastName === "") {
        $("#last_name").siblings(".error").text("Last Name is required.");
        valid = false;
      } else if (!/^[a-zA-Z\s]+$/.test(lastName)) {
        $("#last_name")
          .siblings(".error")
          .text("Last Name can only contain letters.");
        valid = false;
      }

      // Validate Email
      let email = $("#email").val().trim();
      if (email === "") {
        $("#email").siblings(".error").text("Email is required.");
        valid = false;
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        $("#email").siblings(".error").text("Enter a valid email address.");
        valid = false;
      }

      // Validate Phone Number
      let phone = $("#phone_number").val().trim();
      if (phone === "") {
        $("#phone_number").siblings(".error").text("Phone Number is required.");
        valid = false;
      } else if (!/^\d{10}$/.test(phone)) {
        $("#phone_number")
          .siblings(".error")
          .text("Enter a valid 10-digit Phone Number.");
        valid = false;
      }

      // Validate Address
      let address = $("#address").val().trim();
      if (address === "") {
        $("#address").siblings(".error").text("Address is required.");
        valid = false;
      }

      // Validate Date of Birth
      let dob = $("#date_of_birth").val().trim();
      if (dob === "") {
        $("#date_of_birth")
          .siblings(".error")
          .text("Date of Birth is required.");
        valid = false;
      }

      // Validate State
      let state = $("#state").val();
      if (!state) {
        $("#state").siblings(".error").text("State selection is required.");
        valid = false;
      }

      // Validate District
      let district = $("#district").val();
      if (!district) {
        $("#district")
          .siblings(".error")
          .text("District selection is required.");
        valid = false;
      }

      if (!valid) return;

      let formData = new FormData(this);
      console.log("4");
      $("#submitBtn").prop("disabled", true);
      toggleSpinner(true, "Updating profile...");
      console.log("5");
      $.ajax({
        url: $(this).attr("data-url"),
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        headers: { "X-Requested-With": "XMLHttpRequest" },
        success: function (response) {
          $("#submitBtn").prop("disabled", false);
          console.log("6");
          if (response.success && response.html) {
            console.log("7");
            $("#main-content").html(response.html);
            console.log("8");
            new WOW().init();
            initUpdateProfileForm();
            console.log("9");
            $("#ajaxResponseMessage").html(`
                            <div class="alert alert-success alert-dismissible fade show mt-3" role="alert">
                                ${response.message}
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            </div>
                        `);
          } else {
            $("#ajaxResponseMessage").html(`
                            <div class="alert alert-danger alert-dismissible fade show mt-3" role="alert">
                                ${
                                  response.message ||
                                  "Update failed. Try again."
                                }
                                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                            </div>
                        `);
          }
        },
        error: function () {
          $("#submitBtn").prop("disabled", false);
          $("#ajaxResponseMessage").html(`
                        <div class="alert alert-danger alert-dismissible fade show mt-3" role="alert">
                            Something went wrong. Please try again.
                            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                    `);
        },
        complete: function() {
          toggleSpinner(false);
        }
      });
    });

  // Input restrictions
  $("#first_name, #last_name").on("input", function () {
    let cleanValue = $(this)
      .val()
      .replace(/[^a-zA-Z\s]/g, "");
    $(this).val(cleanValue);
  });

  $("#phone_number").on("input", function () {
    let cleanValue = $(this).val().replace(/\D/g, "");
    $(this).val(cleanValue.slice(0, 10)); // Limit to 10 digits
  });
}