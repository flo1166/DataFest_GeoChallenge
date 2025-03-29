import React from 'react';
import OpenStreetMap from './OpenStreetMap';

const App = () => {
  return (
    <div className="app">
      <OpenStreetMap />
      
      <style jsx>{`
        .app {
          width: 100%;
          height: 100vh;
          position: relative;
          margin: 0;
          padding: 0;
          overflow: hidden;
        }
        
        /* Reset global styles */
        :global(body) {
          margin: 0;
          padding: 0;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
            Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
          overflow: hidden;
        }
        
        :global(*) {
          box-sizing: border-box;
        }
      `}</style>
    </div>
  );
};

export default App;