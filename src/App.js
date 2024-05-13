import logo from "./logo.svg";
import "./App.css";
import { GoogleOAuthProvider } from "@react-oauth/google";
import Auth from "./auth/auth";
import React from "react";
function App() {
  return (
    <div className="App">
      <header className="App-header">
        <GoogleOAuthProvider clientId="227194517241-7ja3o4kt1b4hc111u76cl5pbf08b40i9.apps.googleusercontent.com">
          <Auth></Auth>
        </GoogleOAuthProvider>
      </header>
    </div>
  );
}

export default App;
