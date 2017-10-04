import React, { Component } from 'react';
import axios from 'axios';
import logo from './logo.svg';
import './App.css';

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      message: 'hello',
    };
  }

  componentDidMount() {
    // Save 'this'
    let self = this;
    axios.get('/api')
      .then(function(res) {
        console.log(res.data.message);
        self.setState({
          message: res.data.message,
        });
      })
      .catch(function(err) {
        console.log(err);
      });
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">Welcome to React</h1>
        </header>
        <p className="App-intro">
          To get started, edit <code>src/App.js</code> and save to reload.
          {this.state.message}
        </p>
      </div>
    );
  }
}

export default App;
