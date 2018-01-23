// from clusterize.js 
function table_clusterize(data,sID,cID){
    $(".clusterize-scroll").css("max-height", $('body').height() * 0.7);
    
    var clusterize = new Clusterize({
        rows: data.map(function(row) {
            return "<tr>" + row.map(function(col) { return '<td class="uk-text-small uk-text-muted">' + col + '</td>' }).join(" ") + "</tr>"
        }),
        scrollId: sID,
        contentId: cID
    });
}
$("#get_points").click( function () {
    table_clusterize(toolpath,'scrollArea-toolpath','contentArea-toolpath')
});



/* =============  UI function  ============= */




// отправляем на сервер g-code и получаем все состояния регистра по каждому кадру УП!!!
$("#get_parsing_result").click(function () {
    $.ajax({
        type: "POST",
        url: "/get_parsing_result",
        //dataType: "json",
        contentType: "application/json",
        cache: false,
        async: true,
        data: JSON.stringify( { 'gcode' : $("#g-code").val()} ),
        success: function (response) {
            table_clusterize(response,'scrollArea','contentArea')
        },
        error: function(error) {
            console.log(error);
        }
    });
});