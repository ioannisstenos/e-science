// Application routes
App.Router.map(function() {
        this.route('homepage');
        this.resource('user', function() {
		// /user/login
                this.route('login');
                // /user/logout
				this.route('logout');
		// /user/welcome
                this.route('welcome');
        });
        this.resource('cluster', function() {
		// /cluster/create
		this.route('create');
		// /cluster/confirm
                this.route('confirm');
        });
        // Route to enforce login policy
	// other routes that require login extend this
        this.route('restricted');
});