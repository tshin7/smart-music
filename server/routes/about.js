// About page
let User = require('../models/user.js');

const about = (app, isLoggedIn) => {
  const renderHome = (req, res) => {
    res.render('about.ejs', {
      user: req.user // get the user out of session and pass to template
    });
  };

  app.get('/about', isLoggedIn, renderHome);

  return app;
}

module.exports = about
