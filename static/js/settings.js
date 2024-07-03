function change_password() {
    $.ajax({
        type: "POST",
        url: "/change_password",
        data: {
            old_password: $("#OldPassword").val(),
            new_password: $("#NewPassword").val(),
        },
        // nhận dữ liệu từ server json
        success: function(data) {
            if (data.status == "success") {
                alert(data.message);
                window.location = "/login";
            } else {
                alert(data.message);
            }
        },
    });
}

