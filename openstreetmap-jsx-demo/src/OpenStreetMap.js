import React, { useEffect, useRef, useState } from 'react';

// Main OpenStreetMap Component
const OpenStreetMap = () => {
  const mapContainerRef = useRef(null);
  const mapRef = useRef(null);
  const markersRef = useRef([]);
  const [coordinates, setCoordinates] = useState([51.505, -0.09]);
  const [zoom, setZoom] = useState(13);
  const [isMapLoaded, setIsMapLoaded] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Predefined locations
  const locations = {
    berlin: { center: [52.5100, 13.4000], zoom: 12, label: "Berlin" },
    bremen: { center: [53.075, 8.807], zoom: 13, label: "Bremen" },
    cologne: { center: [50.9383, 6.9599], zoom: 12, label: "Cologne" },
    dortmund: { center: [51.5142, 7.4652], zoom: 11, label: "Dortmund" },
    dresden: { center: [51.0493, 13.7381], zoom: 12, label: "Dresden" },
    duisburg: { center: [51.4349, 6.7595], zoom: 13, label: "Duisburg" },
    duesseldorf: { center: [51.225, 6.7763], zoom: 13, label: "Düsseldorf" },
    essen: { center: [51.4582, 7.0158], zoom: 12, label: "Essen" },
    frankfurt: { center: [50.1106, 8.6820], zoom: 11, label: "Frankfurt" },
    hamburg: { center: [53.5503, 10.0006], zoom: 12, label: "Hamburg" },
    hannover: { center: [52.3744, 9.7385], zoom: 13, label: "Hannover" },
    leipzig: { center: [51.3406, 12.3747], zoom: 12, label: "Leipzig" },
    munich: { center: [48.1371, 11.5753], zoom: 12, label: "Munich" },
    nuremberg: { center: [49.4538, 11.0772], zoom: 12, label: "Nuremberg" },
    stuttgart: { center: [48.7784, 9.1800], zoom: 12, label: "Stuttgart" }
  };

  // Load Leaflet scripts and styles
  useEffect(() => {
    // Skip if already loaded
    if (window.L) {
      setIsMapLoaded(true);
      return;
    }

    // Create link for Leaflet CSS
    const linkElement = document.createElement('link');
    linkElement.rel = 'stylesheet';
    linkElement.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
    linkElement.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
    linkElement.crossOrigin = '';
    document.head.appendChild(linkElement);

    // Create script for Leaflet JS
    const scriptElement = document.createElement('script');
    scriptElement.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
    scriptElement.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
    scriptElement.crossOrigin = '';
    scriptElement.onload = () => {
      setIsMapLoaded(true);
    };
    document.head.appendChild(scriptElement);

    // Cleanup function
    return () => {
      document.head.removeChild(linkElement);
      if (document.head.contains(scriptElement)) {
        document.head.removeChild(scriptElement);
      }
      if (mapRef.current) {
        mapRef.current.remove();
      }
    };
  }, []);

  // Initialize map when Leaflet is loaded
  useEffect(() => {
    if (!isMapLoaded || !mapContainerRef.current) return;

    // Initialize map if not already created
    if (!mapRef.current) {
      const L = window.L; // Get Leaflet from window object
      mapRef.current = L.map(mapContainerRef.current, {
        zoomControl: false // Disable default zoom control to add custom position
      }).setView(coordinates, zoom);
      
      // Add custom tile layer for a cleaner "Flächenatlas" style
      L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
      }).addTo(mapRef.current);

      // Add zoom control to bottom right
      L.control.zoom({
        position: 'bottomright'
      }).addTo(mapRef.current);

      // Add event listener for map clicks
      mapRef.current.on('click', handleMapClick);
      
      // Update coordinates and zoom when map is moved
      mapRef.current.on('moveend', () => {
        const center = mapRef.current.getCenter();
        setCoordinates([center.lat, center.lng]);
        setZoom(mapRef.current.getZoom());
      });
      
      // Add initial marker for current location
      addMarker(coordinates, "Starting Location");
    }
  }, [isMapLoaded]);

  // Update map view when coordinates or zoom changes
  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.setView(coordinates, zoom);
    }
  }, [coordinates, zoom]);

  // Function to add a marker to the map (for Flächenatlas style)
  const addMarker = (position, popupText) => {
    if (!mapRef.current || !window.L) return;
    
    const L = window.L; // Get Leaflet from window object
    
    // Create a polygon instead of a standard marker for the Flächenatlas look
    // Creating a hexagon around the point
    const radius = 300; // meters
    const sides = 6;
    const startAngle = 0;
    
    const vertices = [];
    for (let i = 0; i < sides; i++) {
      const angle = startAngle + i * 2 * Math.PI / sides;
      const lat = position[0] + (radius / 111000) * Math.cos(angle);
      const lng = position[1] + (radius / (111000 * Math.cos(position[0] * Math.PI / 180))) * Math.sin(angle);
      vertices.push([lat, lng]);
    }
    
    const areaPolygon = L.polygon(vertices, {
      color: '#41b6c4',
      fillColor: '#41b6c4',
      fillOpacity: 0.3,
      weight: 2
    }).addTo(mapRef.current);
    
    if (popupText) {
      areaPolygon.bindPopup(popupText).openPopup();
    }
    
    markersRef.current.push(areaPolygon);
    return areaPolygon;
  };

  // Handle map clicks to add area markers (for Flächenatlas style)
  const handleMapClick = (e) => {
    if (!mapRef.current || !window.L) return;
    
    const { lat, lng } = e.latlng;
    const position = [lat, lng];
    
    // Create a circle to represent an area of interest
    const L = window.L;
    const areaCircle = L.circle(position, {
      radius: 500,  // 500 meters radius
      color: '#3388ff',
      fillColor: '#3388ff',
      fillOpacity: 0.2,
      weight: 2
    }).addTo(mapRef.current);
    
    // Add popup with coordinates
    const popupText = `Area at ${lat.toFixed(4)}, ${lng.toFixed(4)}`;
    areaCircle.bindPopup(popupText).openPopup();
    
    // Store the circle in markers reference for later cleanup
    markersRef.current.push(areaCircle);
  };

  // Function to clear all markers
  const clearMarkers = () => {
    if (mapRef.current) {
      markersRef.current.forEach(marker => {
        mapRef.current.removeLayer(marker);
      });
      markersRef.current = [];
    }
  };

  // Function to navigate to a location
  const navigateTo = (locationKey) => {
    const location = locations[locationKey];
    setCoordinates(location.center);
    setZoom(location.zoom);
    
    // Clear existing markers and add a new one
    clearMarkers();
    setTimeout(() => {
      addMarker(location.center, location.label);
    }, 100);

    // Auto-close sidebar on mobile after selecting a location
    if (window.innerWidth < 768) {
      setIsSidebarOpen(false);
    }
  };

  // Toggle sidebar
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };
  
  // Add a legend to explain the map elements
  useEffect(() => {
    if (isMapLoaded && mapRef.current && window.L) {
      const L = window.L;
      
      // Create a legend control
      const legend = L.control({position: 'bottomright'});
      
      legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'info legend');
        div.innerHTML = `
          <div style="background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 1px 5px rgba(0,0,0,0.2);">
            <div style="margin-bottom: 8px; font-weight: bold;">Legend</div>
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
              <span style="display: inline-block; width: 16px; height: 16px; background-color: #41b6c4; opacity: 0.3; border: 2px solid #41b6c4; margin-right: 8px;"></span>
              City Marker
            </div>
            <div style="display: flex; align-items: center;">
              <span style="display: inline-block; width: 16px; height: 16px; background-color: #3388ff; opacity: 0.2; border: 2px solid #3388ff; margin-right: 8px;"></span>
              Clicked Area
            </div>
          </div>
        `;
        return div;
      };
      
      legend.addTo(mapRef.current);
      
      return () => {
        legend.remove();
      };
    }
  }, [isMapLoaded]);

  return (
    <div className="map-container">
      {/* Map */}
      <div 
        ref={mapContainerRef} 
        id="map" 
        style={{ 
          height: '100vh', 
          width: '100%',
        }}
      >
        {!isMapLoaded && <div className="loading">Loading map...</div>}
      </div>

      {/* Toggle button */}
      <button 
        className="toggle-sidebar-button"
        onClick={toggleSidebar}
        aria-label="Toggle city selection"
      >
        {isSidebarOpen ? "×" : "☰"}

        
      </button>

      {/* Sidebar */}
      <div className={`sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-content">
          <h2>Area Selection</h2>
          <div className="city-list">
            {Object.keys(locations).map(loc => (
              <button
                key={loc}
                onClick={() => navigateTo(loc)}
                className="city-button"
              >
                {locations[loc].label}
              </button>
            ))}
          </div>
          <button onClick={clearMarkers} className="clear-button">
            Clear All Areas
          </button>
        </div>
      </div>
      
            

      {/* Coordinates display */}
      <div className="coordinates-display">
        {coordinates[0].toFixed(4)}, {coordinates[1].toFixed(4)} | Zoom: {zoom}
      </div>

      <style jsx>{`
        .map-container {
          position: relative;
          width: 100%;
          height: 100vh;
          overflow: hidden;
        }

        .toggle-sidebar-button {
          position: absolute;
          top: 20px;
          left: 20px;
          z-index: 1000;
          width: 50px;
          height: 50px;
          border-radius: 50%;
          background-color: #ffffff;
          color: #333;
          border: none;
          box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
          font-size: 24px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.3s ease;
        }

        .toggle-sidebar-button:hover {
          background-color: #f5f5f5;
        }

        .sidebar {
          position: absolute;
          top: 0;
          left: 0;
          width: 300px;
          height: 100%;
          background-color: #ffffff;
          box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
          z-index: 999;
          transform: translateX(-100%);
          transition: transform 0.3s ease;
          overflow-y: auto;
        }

        .sidebar.open {
          transform: translateX(0);
        }

        .sidebar-content {
          padding: 80px 20px 20px;
        }

        h2 {
          margin-bottom: 20px;
          color: #333;
          font-size: 24px;
          text-align: center;
        }

        .city-list {
          display: flex;
          flex-direction: column;
          gap: 10px;
          margin-bottom: 30px;
        }

        .city-button {
          padding: 12px 15px;
          border: none;
          border-radius: 8px;
          background-color: #f0f2f5;
          color: #333;
          font-size: 16px;
          text-align: left;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .city-button:hover {
          background-color: #e4e6eb;
        }

        .clear-button {
          width: 100%;
          padding: 12px 15px;
          border: none;
          border-radius: 8px;
          background-color: #f44336;
          color: white;
          font-size: 16px;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .clear-button:hover {
          background-color: #d32f2f;
        }

        .loading {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          display: flex;
          justify-content: center;
          align-items: center;
          background-color: rgba(255, 255, 255, 0.8);
          font-size: 20px;
          color: #333;
        }

        .coordinates-display {
          position: absolute;
          bottom: 15px;
          left: 15px;
          padding: 8px 12px;
          background-color: rgba(255, 255, 255, 0.8);
          border-radius: 4px;
          font-size: 14px;
          color: #333;
          z-index: 500;
          box-shadow: 0 1px 5px rgba(0, 0, 0, 0.2);
        }

        /* Responsive styles */
        @media (max-width: 767px) {
          .sidebar {
            width: 80%;
            max-width: 300px;
          }
          
          .toggle-sidebar-button {
            top: 10px;
            left: 10px;
            width: 40px;
            height: 40px;
            font-size: 20px;
          }
          
          .coordinates-display {
            font-size: 12px;
            padding: 6px 10px;
          }
        }
      `}</style>
    </div>
  );
};

export default OpenStreetMap;