/**
 * @author sorseg
 */

atom.declare( 'Caster.Obj', App.Element, {
	
	configure: function () {
		this.bindMethods(['get_cells']);
		this.obj = obj = this.settings.get('obj');
		eng = this.settings.get('engine');
		this.size = obj.size
		from = eng.getCellByIndex(obj.coords).rectangle.from;
		to = eng.getCellByIndex( new Point(obj.coords).move([this.size-1, this.size-1])).rectangle.to
		this.shape = new Rectangle({from:from, to:to});
		/*
		var handler = this.layer.app.resources.get('mouseHandler')
		handler.subscribe(this);
		
		this.clickable = new App.Clickable(this, this.redraw).start();
		*/
	},
	
	renderTo: function (ctx) {
		ctx.save()
		ctx.textBaseline = 'bottom';
		text_opts = {
			text:this.obj.char,
			to: this.shape,
			align:'center',
			size:this.shape.size.x*0.9,
			family:'monospace',
			stroke:false,
			lineWidth:2,
			color:this.settings.get('player')?'red':'#333'
		};
		
		ctx.text(text_opts);
		ctx.restore();
	},
	
	/*
	onUpdate: function(){
		this.redraw();
	},
	*/
	
	get_cells: function(new_coord){
		if (new_coord == undefined){
			new_coord = this.obj.coords;
		}
		return approx_maps[this.size].map(function(c){
			return Point(new_coord).move(c)}.bind(this)); 
	},
	
	
	
});