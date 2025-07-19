// Function to initialize login form JS

// Global loading handlers
$(document).ajaxSend(function() {
  $('body').addClass('global-ajax-loading');
});

$(document).ajaxComplete(function() {
  $('body').removeClass('global-ajax-loading');
});

// Form-specific loading handler
$(document).on('submit', 'form', function() {
  $(this).addClass('form-ajax-loading');
});

$(document).on('ajaxComplete', 'form', function() {
  $(this).removeClass('form-ajax-loading');
});
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

      showLoader();
      
      $.ajax({
        url: $("#loginInfo").attr("action"),
        type: "POST",
        data: $(this).serialize(),
        headers: {
          "X-Requested-With": "XMLHttpRequest",
        },
        success: function (response) {
          hideLoader();
          if (response.success && response.html) {
            // Successful login
            $("#main-content").html(response.html);
            history.pushState({}, "", response.redirect_url);
            new WOW().init();

            // Update navbar
            $.ajax({
              url: "/app/navbar/",
              headers: { "X-Requested-With": "XMLHttpRequest" },
              success: function (data) {
                $(".container-fluid.bg-white.sticky-top").replaceWith(
                  $(data.html).filter(".container-fluid.bg-white.sticky-top")
                );
              },
              error: function () {
                console.error("Failed to update navbar.");
              },
            });
          } else if (response.message) {
            // Handle error messages
            displayMessage(response.message, "danger");
            // Update captcha if provided
            if (response.captcha) {
              $("#captchaImage").html(response.captcha);
            }
          } else {
            displayMessage("Unexpected response from server.", "danger");
          }
        },
        error: function () {
          hideLoader();
          displayMessage("Something went wrong. Try again.", "danger");
        },
      });

      return false;
    });

  // Captcha refresh button
  $("#refreshCaptchaBtn")
    .off("click")
    .on("click", function () {
      showLoader();
      $.ajax({
        url: refreshCaptchaUrl,
        type: "GET",
        success: function (data) {
          if (data.captcha_code) {
            $("#captchaImage").html(data.captcha_code);
          } else if (data.captcha) {
            $("#captchaImage").html(data.captcha);
          }
        },
        error: function (xhr, status, error) {
          hideLoader();
          console.error("Error:", status, error);
          let msg = "Something went wrong. Try again.";
          if (xhr.responseJSON && xhr.responseJSON.message) {
            msg = xhr.responseJSON.message;
          }
          displayMessage(msg, "danger");
        },
        complete: function () {
          hideLoader();
        },
      });
    });


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
}

// AJAX page loading function
function loadPage(url) {
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

      // Initialize login form if login page loaded
      if (url.includes("/login")) {
        initLoginForm();
      }
    },
    error: function () {
      alert("Failed to load page.");
    },
  });
}

$(document).ready(function () {
  new WOW().init();

  if (window.location.pathname.includes("/login")) {
    initLoginForm();
  }

  // Handle navbar link clicks with AJAX load
  $(document).on(
    "click",
    ".navbar-nav a#nav-item.nav-link, .navbar-nav .dropdown-menu a.dropdown-item",
    function (e) {
      e.preventDefault();

      var url = $(this).attr("href");
      if (url === window.location.pathname) {
        return; // already on page
      }

      loadPage(url);
      //   history.pushState(null, null, url);
    }
  );

  // Handle back/forward buttons
  window.onpopstate = function () {
    loadPage(location.pathname);
  };
});



$(document).on('click', '#logoutButton', function(e) {
    e.preventDefault();
    
    $.ajax({
        url: '/app/logout/',
        type: 'POST',
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val()
        },
        success: function(response) {
            if (response.redirect) {
                // Option 1: Full redirect (simplest)
                // window.location.href = response.redirect;
                
                // Option 2: SPA-style update (no page reload)
                loadPage(response.redirect);  // Use your existing loadPage function
                history.pushState({}, '', response.redirect);
                
                // Optional: Update navbar to show logged-out state
                $.ajax({
                    url: '/app/navbar/',
                    headers: { "X-Requested-With": "XMLHttpRequest" },
                    success: function(data) {
                        $(".container-fluid.bg-white.sticky-top").replaceWith(
                            $(data.html).filter(".container-fluid.bg-white.sticky-top")
                        );
                    }
                });
            }
        },
        error: function() {
            displayMessage("Logout failed. Please try again.", "danger");
        }
    });
});