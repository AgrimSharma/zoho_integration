

$(".sign_in").click(function () {
   var user_name = $("#login-username").val();
   var password = $("#login-password").val();
   if(user_name !== "" && password !== ""){
       $.ajax({
        type: "POST",
        url: "/login_user/",
        data: {
            'username': user_name,
            "password": password
        },
        success: function(resp) {
          var data = JSON.parse(resp);
          if (data.message === 'success') {
              window.location.href = "/clients/";
          } else {
              alert("Please try again")
          }

        }

      });
   }
   else {
       alert("Password or Email can't be blank");
   }
});

    $("#btn-signup").click(function () {
       var user_name = $("#username").val();
       var email = $("#email").val();
       var password = $("#password").val();
       if(password !== "" || user_name !== "" || email !== ""){
           $.ajax({
            type: "POST",
            url: "/register_user/",
            data: {
                'username': user_name,
                "email": email,
                "password": password
            },

            success: function(resp) {
              var data = JSON.parse(resp);
              if (data.message === 'success') {
                  // alert('success');
                    window.location.href = "/";
              } else {
                  alert("User name or Email already taken");
              }

            }

          });
       }
       else {
           alert("Password and Confirm Password should be same");
       }
    });

