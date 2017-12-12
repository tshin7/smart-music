// Start page
let User = require('../models/user.js');

const home = (app, isLoggedIn) => {
  const renderHome = (req, res) => {
    res.render('home.ejs', {
      user: req.user // get the user out of session and pass to template
    });
  };

  app.get('/home', ,isLoggedIn, renderHome);

  return app;
}

module.exports = home
