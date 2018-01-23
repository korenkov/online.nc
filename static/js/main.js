// scene (global parameters: use in 'load_examples.js' / 'draw.js' / 'checkout.js')
var scene = new THREE.Scene();


$(document).ready(function(){

// get scene size: width = width card | height = full page - header
var SCREEN_WIDTH = $('#webgl').width();
var SCREEN_HEIGHT = $('#webgl').height();
//var SCREEN_HEIGHT = $('body').height() - 30;
$('#webgl').height(SCREEN_HEIGHT); /* set card height = full page - header */

// check support WebGl in browser
if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

// renderer (set "WebGLRenderer" or "CanvasRenderer")
var haswebgl = (function() {
    try { 	return !! window.WebGLRenderingContext && !! document.createElement('canvas').getContext('experimental-webgl'); }
    catch(e){ return false; }
})();
if (haswebgl) renderer = new THREE.WebGLRenderer( { antialias: true, alpha: true } ); 
else renderer = new THREE.CanvasRenderer();

renderer.setSize( SCREEN_WIDTH, SCREEN_HEIGHT );
$("#webgl").append(renderer.domElement);

// camera
var camera = new THREE.PerspectiveCamera( 45, SCREEN_WIDTH / SCREEN_HEIGHT, 0.1, 20000 );
camera.position.set( -50, -200, 200 );
//camera.lookAt(scene.position);
  
// controls
controls = new THREE.TrackballControls( camera, renderer.domElement );
controls.rotateSpeed = 5.0;
controls.zoomSpeed = 5.0;
controls.panSpeed = 3.0;
controls.noZoom = false;
controls.noPan = false;
controls.staticMoving = true;
controls.dynamicDampingFactor = 0.5;
controls.keys = [ 65, 83, 68 ];
    
// lights
light = new THREE.DirectionalLight( 0xffffff );
light.position.set( -200, -200, 400 );
scene.add( light );
light = new THREE.DirectionalLight( 0xD1D7FF );
light.position.set( 200, -100, -100 );
scene.add( light );
light = new THREE.AmbientLight( 0x222222 );
scene.add( light );

// changes and resize windiw
controls.addEventListener( 'change', render );
window.addEventListener( 'resize', onWindowResize, false );

function onWindowResize() {
    SCREEN_WIDTH = $('#webgl').width();
    SCREEN_HEIGHT = $('#webgl').height();
    //SCREEN_HEIGHT = $('body').height() - 100;
    //$('#webgl').height(SCREEN_HEIGHT);

    camera.aspect = SCREEN_WIDTH / SCREEN_HEIGHT;
    camera.updateProjectionMatrix();
    renderer.setSize( SCREEN_WIDTH, SCREEN_HEIGHT );
    controls.handleResize();
    render();
}

// call after draving !!!
function animate() {
    requestAnimationFrame( animate );
    controls.update();
    render();
}

function render() {
//	renderer.clear();	
    renderer.render( scene, camera );
}

animate();

}); //main $(document).ready