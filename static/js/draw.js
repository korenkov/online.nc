// global variable
var toolpath = [];
var remove_elements = [];


/* ----------------- drawing environment ----------------- */
function drawing_environment(Object3D){
    // get bounding box coordinates
    var bbox = new THREE.Box3().setFromObject(Object3D);
    var height = bbox.max['z'] - bbox.min['z'];
    var width = bbox.max['y'] - bbox.min['y'];
    var depth = bbox.max['x'] - bbox.min['x'];
    var axes_scale = Math.min(height, width, depth) / 2;

    // bounding box
    /*
    var helper = new THREE.BoxHelper(line, 0xffff00 );
    helper.update();
    helper.position.set( -1, -1, -1 );
    scene.add(helper);
    */
    // axes
    var axes = new THREE.AxesHelper( axes_scale );
    scene.add( axes );
    
    // plan XY
    var geometry = new THREE.PlaneGeometry(depth * 2, width * 2);
    //var material = new THREE.MeshBasicMaterial( {color: 0x41b8f4, transparent: true, opacity: 0.6, side: THREE.DoubleSide} );
    var material = new THREE.ShadowMaterial( { opacity: 0.2 } );
    var plane = new THREE.Mesh( geometry, material );
    plane.receiveShadow = true;
    plane.position.z = -axes_scale / 10;
    scene.add( plane );
    
    // grid
    var grid = new THREE.GridHelper( depth * 2, width*2 );
    grid.position.y = -axes_scale / 10;
    grid.rotateX( - Math.PI / 2 );
    grid.material.opacity = 0.25;
    grid.material.transparent = true;
    scene.add( grid );
    
    //remove_elements.push(helper);
    remove_elements.push(axes);
    remove_elements.push(plane);
    remove_elements.push(grid);
};


/* ----------------- clear scene -----------------  */
function clear(){
    for(var i=0; i < remove_elements.length;i++) {
        //remove_elements[i].geometry.dispose();
        //remove_elements[i].material.dispose();
        scene.remove(remove_elements[i]);
    };
    remove_elements = [];
    toolpath = [];
};


/* ----------------- drawing toolpath -----------------  */
function drawing_toolpath() {
    var points = new THREE.Geometry();
    for (var i = 0; i < toolpath.length; i++) {
        points.vertices.push( new THREE.Vector3(toolpath[i][0], toolpath[i][1], toolpath[i][2]) );
    }; // For
    var line = new THREE.Line( points, new THREE.LineBasicMaterial( { color: 0xf4cd41, opacity: 1.0 } ) );
    scene.add( line );
    
    remove_elements.push(points);
    remove_elements.push(line);
    
    drawing_environment(line);
};

function get_coordinates(response, callback){
    //console.log(response);
    for (var i=0; i<response.length; i++) {
        toolpath.push([response[i][0].toFixed(3), response[i][1].toFixed(3), response[i][2].toFixed(3), response[i][3].toFixed(1), response[i][4].toFixed(1)]);
    };
    callback();
};

// отправляем на сервер g-code и получаем только x-y-z-f-s !!!
$("#send_gcode").click(function () {
    clear();
    
    $.ajax({
        type: "POST",
        url: "/get_xyz",
        //dataType: "json",
        contentType: "application/json",
        cache: false,
        async: true,
        data: JSON.stringify( { 'gcode' : $("#g-code").val()} ),
        success: function (response) {
           get_coordinates(response, drawing_toolpath);
        },
        error: function(error) {
            console.log(error);
        }
    });
});
