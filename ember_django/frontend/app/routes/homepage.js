App.HomepageRoute = Ember.Route.extend({
    news_items : [],
    actions : {
        didTransition : function(transition) {
            var that = this;
            // Perform GET request for cluster statistics
            this.store.fetch('statistic', 1).then(function(statistic) {
                that.controller.set('spawned_clusters', statistic.get('spawned_clusters'));
                that.controller.set('active_clusters', statistic.get('active_clusters'));
            }, function(reason) {
                console.log(reason.message);
            });
            // Perform GET request for news items
            this.store.fetch('newsitem', {}).then(function(newsitem) {
                that.controller.set('news_items', newsitem.get('content'));
            }, function(reason) {
                console.log(reason.message);
            });
        }
		//didTransition : function(transition) {
			//var that = this;
			//// Perform GET request for images
			//this.store.fetch('okeanosimage', {}).then(function(images) {
			//	console.log(images.get('content'));
			//}, function(reason) {
			//	console.log(reason.message);
			//});
		//}
    }
});
