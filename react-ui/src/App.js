import React, { Component } from 'react';
import axios from 'axios';
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
      <div>
        <h1>Smart Music</h1>
      </div>
    );
  }
}

export default App;
