/**
 * @author sorseg
 * 
 * TODO: map -> forEach
 * TODO: view panning
 */

var models = {"kob1":"@",
		  "drak1":"&",
		  "sword":")",
		  "wall":"#",
		  "floor":"." };


var approx_maps = [
	[],
	[[0, 0]],
	[[0, 0], [0, 1], [1, 0], [1, 1]],
	[[0, 0], [0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]],
	[[0, 1], [0, 2], [1, 0], [1, 1], [1, 2], [1, 3], [2, 0], [2, 1], [2, 2], [2, 3], [3, 1], [3, 2]],
	[[0, 1], [0, 2], [0, 3], [1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [3, 0], [3, 1], [3, 2], [3, 3], [3, 4], [4, 1], [4, 2], [4, 3]]]

atom.declare( 'Caster.Controller', {
	
	initialize: function () {
		console.log('Initiating controller');
		this.bindMethods(['environment','responses','add_object'])
		this.app = null;
		this.size = new Size([0,0]);
		
		this.objects = {};
		this.terrain = [];
		this.all_x = [];
		this.all_y = [];
		
		this.network_controller = new Caster.Network(this);
		this.view = new Caster.View(this);
		
		this.reactions = ['login', 'joined', 'environment', 'responses'];
		this.creatures = {};
		
		this.requests = [];
		this.turn_number = -1;
		
		this.network_controller.connect();
	},
	
	login: function(obj) {
		this.view.login(obj);
		obj.creatures.forEach(function(crtr){
			this.creatures[crtr.id] = crtr;
		}.bind(this));
	},
	
	joined: function(obj){
		this.joined_crid = obj.crid;
		this.view.joined(this.creatures[obj.crid]);
	},
	
	environment: function(obj){
		this.update_turn_n(obj.turn);
		for(var i=0; i<obj.cells.length; i++){
			c = obj.cells[i].coords
			this.all_x.push(c[0])
			this.all_y.push(c[1])
		}
		
		if (this.all_x.length == 0){
			console.log("Empty coords");
			return;
		}
		var sortf = function(a,b){return a-b;};
		this.all_x.sort(sortf);
		this.all_y.sort(sortf);
		
		var xmax = this.all_x[this.all_x.length-1];
		var xmin = this.all_x[0];
		
		var ymax = this.all_y[this.all_y.length-1];
		var ymin = this.all_y[0];
	
		this.size = new Size(new Point(xmin, ymin).diff(new Point(xmax+1, ymax+1)));
		 
		this.create_app();
		
		obj.cells.forEach(function(c){
			this.engine.getCellByIndex(c.coords).value = models[c.type];
			//offset all coords by starting position
			p = new Point(xmin, ymin).diff(new Point(c.coords));
			if (typeof(this.terrain[p.y]) == 'undefined'){
				this.terrain[p.y] = [];
			}
			this.terrain[p.y][p.x] = c;
		}.bind(this));
		
		obj.objects.forEach(this.add_object);
		
	},
	
	create_app: function(){
		var tile_opts = {
			size: this.size,
			cellSize: new Size(20, 20),
			cellMargin: new Size(1,1),
			defaultValue: '?'
		}
		
		this.engine = new TileEngine(tile_opts).setMethod({'#':this.draw.bind(this,'#333'),
					  '.':this.draw.bind(this, '#444'),
					  '?':this.draw.bind(this, '#000')}
					  );
		
		tile_opts.defaultValue = 0;
		
		
		this.app = new App({
			size: this.engine.countSize(),
			appendTo: '#field'
		});	
		
		var mouse, mouseHandler;
		mouse = new Mouse(this.app.container.bounds);
		mouseHandler = new App.MouseHandler({ mouse: mouse, app: this.app });
		
		this.cell_layer = this.app.createLayer({name:'cells', zIndex:0});
		this.cell_overlay = this.app.createLayer({name:'overlay', zIndex:1});
		this.object_layer = this.app.createLayer({name:'objects', zIndex:2});
		
		this.overlay_engine = new TileEngine(tile_opts).setMethod({0:'rgba(0,0,0,0)',
																	1:'rgba(0,255,0,0.1)',
																	2:'rgba(255,0,0,0.1)'});
		this.overlay_element = new TileEngine.Element( this.cell_overlay, {engine:this.overlay_engine} );
		
		this.element = TileEngine.Element( this.cell_layer, {engine:this.engine} );
		
		mouseHandler.subscribe(this.element)
		mouse.events.add( 'contextmenu', Mouse.prevent );
		this.tile_mouse = new TileEngine.Mouse( this.element, mouse ).events
			.add( 'click', function (cell, e) {
				this.click(cell, e.button);
			}.bind(this))
			.add( 'over', this.hover.bind(this, true))
			.add( 'out', this.hover.bind(this, false));
		
		
	},
	
	responses: function(obj){
		this.update_turn_n(obj.turn);
		obj.new_objects.forEach(this.add_object);
	},
	
	click: function(cell, b){
		//to reset hovered cells
		this.hover(false, cell);
		if(this.action != 'move'){
			return;
		}
		if(b==0){
			this.request_move(cell);
		}
		this.view.reset_action();
	},
	
	sep_color:'#222',
	
	draw: function (color, ctx, cell) {
		ctx.fill(cell.rectangle, color);
		for (var m = 0; m<2; m++){
				coord_diff = [[-1,0],[0,-1]][m];
				neigh_coord = cell.point.clone().move(coord_diff);
				neigh_cell = cell.engine.getCellByIndex(neigh_coord);
				if ((neigh_cell != null) && (neigh_cell.value != cell.value)){
					from = cell.rectangle.from;
					to = coord_diff[1]?cell.rectangle.topRight:cell.rectangle.bottomLeft;
					ctx.save()
					.set({ lineWidth: 2 })
					.stroke(new Line(from, to), this.sep_color)
					.fill(new Rectangle({center:from,size:[2,2]}), this.sep_color)
					.fill(new Rectangle({center:to,size:[2,2]}), this.sep_color)
					.restore();
				}
		}
		if(typeof(cell.value) == 'string'){
		ctx.text({
		text:cell.value,
		to: cell.rectangle,
		align:'center',
		size:15,
		family:'monospace'
		});
		};
	},
	
	hover: function(over, cell){
		if(over){
			this.view.update_coords(cell.point);
		}
		

		var cc = this.calc_cells(cell.point);
		cc.forEach(function(p){
			try{
				color = (this.engine.getCellByIndex(p).value != '.')?2:1;
				this.overlay_engine.getCellByIndex(p).value = (over && (this.action == 'move'))?color:0;
			}catch(e){};
		}.bind(this))
	},
	
	add_object: function(obj){
		if (obj.id == undefined){
			console.log('cannot add object without id: '+obj);
			return;
		}
		
		//var rand_color = "#"+((1<<24)*("0."+Math.sin(obj.id).toString().substr(6))|0).toString(16);
		//this.engine.setMethod(obj.id, this.draw.bind(this, rand_color));
		
		this.engine.setMethod(obj.id,
			this.draw.bind(this,
				'hsl('+("0."+Math.sin(obj.id).toString().substr(6))*360+', 40%, 40%)'));
		
		this.objects[obj.id] = new_obj = new Caster.Obj(this.object_layer, {obj:obj,
																			engine:this.engine,
																			player:(obj.id == this.joined_crid)})
		new_obj.obj.char = models[new_obj.obj.model];
		new_obj.get_cells().forEach(function(c){
				this.engine.getCellByIndex(c).value = obj.id;
			}.bind(this));
		return new_obj;
		
	},
	
	calc_cells: function(cell){
		var obj = this.objects[this.joined_crid];
		var line = calcStraightLine(obj.obj.coords, cell);
		var coords = [];
		line.forEach(function(coord){
			coords = coords.concat(obj.get_cells(coord));
		});
		return coords;
	},
	
	update_turn_n: function(n){
		this.turn_number = Math.max(this.turn_number, n);
		this.view.update_turn_n(n);
	},
	
	request_move: function(cell){
		var cc = this.calc_cells(cell.point);
		for(var i=0; i<cc.length; i++){
			if(this.engine.getCellByIndex(cc[i]).value == '#'){
				return;
			}
		}
		
		dir = getDirections(this.objects[this.joined_crid].obj.coords, cell.point);
		for(var i =0; i<dir.length; i++){
			r = {
				what:"request",
				type:"move",
				where:dir[i]
				}
				
			this.add_request(r);
		}
		
		
	},
	
	add_request: function(req){
		req['order'] = this.requests.length+1;
		req['turn'] = this.turn_number+1;
		this.requests.push(req);
		//this.view.add_request(req);
		//send request via websocket
		this.network_controller.send(req);
	},
	
	cancel_request: function(req){
		//find request via order # and remove it from
		this.view.remove_request(req);
	}
	

});