/**
 * @author sorseg
 */

LibCanvas.extract();

function calcStraightLine (startCoordinates, endCoordinates) {
	var coordinatesArray = new Array();
	// Translate coordinates
	var sp = new Point(startCoordinates);
	var ep = new Point(endCoordinates);
	var x1 = sp.x;
	var y1 = sp.y;
	var x2 = ep.x
	var y2 = ep.y;
	// Define differences and error check
	var dx = Math.abs(x2 - x1);
	var dy = Math.abs(y2 - y1);
	var sx = (x1 < x2) ? 1 : -1;
	var sy = (y1 < y2) ? 1 : -1;
	var err = dx - dy;
	// Set first coordinates
	coordinatesArray.push([x1, y1]);
	// Main loop
	while (!((x1 == x2) && (y1 == y2))) {
	  var e2 = err << 1;
	  if (e2 > -dy) {
		err -= dy;
		x1 += sx;
	  }
	  if (e2 < dx) {
		err += dx;
		y1 += sy;
	  }
	  // Set coordinates
	  coordinatesArray.push([x1, y1]);
	}
	// Return the result
	return coordinatesArray;
}

function getDirections(p1, p2){

	l = calcStraightLine(p1, p2);
	if (l.length == 0){
		return [];
	}
	
	dir = [];
	for(var i=1; i<l.length;i++){
		dir.push([l[i][0]-l[i-1][0], l[i][1]-l[i-1][1]]);
	}
	return dir;
	
}
