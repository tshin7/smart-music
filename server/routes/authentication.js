const authentication = (app, passport) => {
  // show the signup page
  const renderSignupPage = (req, res) => {
    // render the page and pass in any flash data if it exists
    res.render('signup.ejs', { message: req.flash('signupMessage') });
  };

  // process the signup form
  const processSignup = passport.authenticate('local-signup', {
    successRedirect : '/home', // redirect to the secure profile section
    failureRedirect : '/signup', // redirect back to the signup page if there is an error
    failureFlash : true // allow flash messages
  });

  // show the login page
  const renderLoginPage = (req, res) => {
    // render the page and pass in any flash data if it exists
    res.render('login.ejs', { message: req.flash('loginMessage') });
  };

  // process login
  const processLogin = passport.authenticate('local-login', {
    successRedirect: '/home', // redirect to the secure profile section
    failureRedirect: '/login', // redirect back to the signup page if there is an error
    failureFlash: true // allow flash messages
  });

  // logout user
  const logoutUser = (req, res) => {
    req.logout();
    res.redirect('/');
  };

  app.get('/signup', renderSignupPage);
  app.post('/signup', processSignup);
  app.get('/login', renderLoginPage);
  app.post('/login', processLogin);
  app.get('/logout', logoutUser);

  return app;
};

module.exports = authentication
