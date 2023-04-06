function req_get_title(id){
    $.ajax({
        url: "get_title",
        type: "GET", // для метода гет
//        type: "POST", // для метода пост
        data: {link: document.getElementById("link").value, btn_id: id},
        dataType : "text",
        success : function(result) {
            console.log("success");
            document.getElementById("title").value = result;},
        error : function(xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
            }
    });
}
