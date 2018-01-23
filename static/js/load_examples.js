// LOAD EXAMPLES

// --------------- example 01: Finish 2D contour milling --------------- //

$("#load_example_01").click( function () {
    $.ajax({
        url : "/static/examples/O0001.txt",
        dataType: "text",
        success : function (data) {
            $("#g-code").text(data);
        }
    });
});

// --------------- example 02: 3D Printing --------------- //

$("#load_example_02").click( function () {
    $.ajax({
        url : "/static/examples/O0002.txt",
        dataType: "text",
        success : function (data) {
            $("#g-code").text(data);
        }
    });
});


// --------------- example 03: 3D surface milling (3D & toolpath) --------------- //
$("#load_example_03").click( function () {
    $.ajax({
        url : "/static/examples/O0003.txt",
        dataType: "text",
        success : function (data) {
            $("#g-code").text(data);
        }
    });
	
	var loader = new THREE.STLLoader();
	loader.load( '/static/examples/test_part2.STL', function ( geometry ) {
		var material = new THREE.MeshPhongMaterial( { color: 0xCCCCCC, transparent: true, opacity: 0.5, specular: 0x111111, shininess: 200 } );
		var work = new THREE.Mesh( geometry, material );
		work.position.set( 0, 0, 0 );
		work.rotation.set( 0, 0, 0 );
		work.scale.set( 1.0, 1.0, 1.0 );
		work.castShadow = true;
		work.receiveShadow = true;
		scene.add( work );
		// wireframe
		/*
		var wireframeMaterial = new THREE.MeshBasicMaterial( { color: 0x000000, wireframe: true, transparent: true } );
		var work_wire = work.clone();
		work_wire.material = wireframeMaterial ;
		//work_wire.material.needsUpdate = true;
		scene.add( work_wire );
		*/
	} );
});