module('Integration Tests - Routes', {
	setup: function(){
		
	},
	teardown: function() {
    App.reset();
	}
});

test('root_route_redirects_to_homepage', function() {
  expect(1); // Ensure that we will perform one assertion

  visit('/');
  // Wait for asynchronous helpers above to complete
  andThen(function() {
    equal(currentRouteName(), 'homepage');
  });
});

test('protected_resources_redirects_to_login', function() {
  expect(2);
  visit('/cluster/create');
  andThen(function() {
    equal(currentRouteName(), 'user.login');
  });
  visit('/user/welcome');
  andThen(function() {
    equal(currentRouteName(), 'user.login');
  })
});