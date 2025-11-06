import React, { useState, useEffect, useRef } from "react";
import { Car, MapPin, Users, Clock, Check, X } from "lucide-react";

interface Node {
  id: string;
  name: string;
  lat: number;
  lng: number;
}

interface Edge {
  u: string;
  v: string;
  weight: number; // ✅ add this field
}

interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

interface Driver {
  id: string;
  location: string;
  status: "idle" | "en-route";
  passengers: Array<{ userId: string }>;
  finalDestination?: string;
}

interface Request {
  id: string;
  userId: string;
  source: string;
  destination: string;
}

interface RideHistory {
  id: string;
  type: string;
  riders: string[];
  driver: string;
  distance: number;
}

interface Route {
  path: string[];
  distance: number;
}

interface Message {
  success: boolean;
  text: string;
}

const API_BASE_URL = "http://127.0.0.1:5000";

export default function App() {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [requests, setRequests] = useState<Request[]>([]);
  const [rideHistory, setRideHistory] = useState<RideHistory[]>([]);
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [selectedDest, setSelectedDest] = useState<string | null>(null);
  const [currentRoute, setCurrentRoute] = useState<Route | null>(null);
  const [userId, setUserId] = useState("");
  const [message, setMessage] = useState<Message | null>(null);
  const [selectionMode, setSelectionMode] = useState<"source" | "dest">("source");

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/status`);
      const data = await res.json();
      setGraphData({ nodes: data.nodes, edges: data.edges });
      setDrivers(data.drivers);
      setRequests(data.requests);
      setRideHistory(data.rideHistory);
    } catch (error) {
      setMessage({ success: false, text: "Cannot connect to backend." });
    }
  };

  const handleNodeClick = (id: string) => {
    if (selectionMode === "source") {
      setSelectedSource(id);
      setSelectionMode("dest");
    } else {
      setSelectedDest(id);
      setSelectionMode("source");
    }
    setCurrentRoute(null);
  };

  const handleSubmit = async () => {
    if (!userId || !selectedSource || !selectedDest) {
      setMessage({ success: false, text: "Please fill all fields." });
      return;
    }
    const res = await fetch(`${API_BASE_URL}/submit-request`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        userId,
        source: selectedSource,
        destination: selectedDest,
      }),
    });
    const data = await res.json();
    setMessage({ success: data.success, text: data.message });
    if (data.assigned_route) setCurrentRoute(data.assigned_route);
    fetchStatus();
    setUserId("");
    setSelectedSource(null);
    setSelectedDest(null);
  };

  const handleComplete = async (driverId: string) => {
    const res = await fetch(`${API_BASE_URL}/complete-ride`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ driverId }),
    });
    const data = await res.json();
    setMessage({ success: data.success, text: data.message });
    fetchStatus();
  };

  const getNodeName = (id: string | null) => {
    const node = graphData.nodes.find((n) => n.id === id);
    return node ? node.name : id;
  };

  return (
    <div className="h-screen flex flex-col font-sans bg-gray-100 text-gray-800">
      {/* Header */}
      <header className="bg-gray-800 text-white p-3 flex items-center gap-2 shadow">
        <Car className="w-6 h-6 text-blue-300" />
        <h1 className="text-lg font-semibold">Smart Carpool System</h1>
      </header>

      {/* Message Box */}
      {message && (
        <div className="fixed top-5 right-5 bg-white border shadow-md rounded-md p-3 flex items-center gap-2 text-sm">
          <span className={message.success ? "text-green-600" : "text-red-600"}>
            {message.text}
          </span>
          <button onClick={() => setMessage(null)}>
            <X size={14} className="text-gray-600" />
          </button>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 grid md:grid-cols-3 gap-2 p-2 overflow-hidden">
        {/* Left Panel */}
        <div className="col-span-1 flex flex-col bg-white border rounded-md shadow-sm p-3 space-y-3 overflow-y-auto">
          <h2 className="font-semibold text-gray-700 text-lg flex items-center gap-2">
            <MapPin className="w-4 h-4 text-blue-600" />
            Request Ride
          </h2>

          <div className="text-sm space-y-1">
            <p className="text-gray-600 flex items-center gap-1">
              <Clock size={14} /> Select {selectionMode === "source" ? "Source" : "Destination"}
            </p>
            <input
              placeholder="User ID"
              className="border w-full rounded px-2 py-1 text-sm"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
            />
            <select
              className="border w-full rounded px-2 py-1 text-sm"
              value={selectedSource || ""}
              onChange={(e) => setSelectedSource(e.target.value)}
            >
              <option value="">Select source</option>
              {graphData.nodes.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.name}
                </option>
              ))}
            </select>
            <select
              className="border w-full rounded px-2 py-1 text-sm"
              value={selectedDest || ""}
              onChange={(e) => setSelectedDest(e.target.value)}
            >
              <option value="">Select destination</option>
              {graphData.nodes.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.name}
                </option>
              ))}
            </select>
            <button
              onClick={handleSubmit}
              className="bg-blue-600 text-white rounded py-1 px-3 w-full mt-2"
            >
              Submit Request
            </button>
          </div>

          <div>
            <h3 className="font-semibold text-gray-700 mt-4">
              Pending Requests ({requests.length})
            </h3>
            <div className="border rounded-md p-2 text-sm bg-gray-50 h-32 overflow-y-auto">
              {requests.length === 0 ? (
                <p className="text-gray-500 text-xs">No pending requests.</p>
              ) : (
                requests.map((r) => (
                  <p key={r.id}>
                    <b>{r.userId}</b>: {getNodeName(r.source)} → {getNodeName(r.destination)}
                  </p>
                ))
              )}
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-gray-700 mt-4">
              Ride History ({rideHistory.length})
            </h3>
            <div className="border rounded-md p-2 text-sm bg-gray-50 h-32 overflow-y-auto">
              {rideHistory.length === 0 ? (
                <p className="text-gray-500 text-xs">No rides yet.</p>
              ) : (
                rideHistory.map((r, i) => (
                  <div key={i} className="border-b py-1 text-xs">
                    {r.type}: {r.riders.join(", ")} via {r.driver} ({r.distance.toFixed(2)} km)
                  </div>
                ))
              )}
            </div>
          </div>

          <div>
            <h3 className="font-semibold text-gray-700 mt-4">
              Drivers ({drivers.length})
            </h3>
            <div className="border rounded-md p-2 text-sm bg-gray-50 h-32 overflow-y-auto">
              {drivers.map((d) => (
                <div
                  key={d.id}
                  className="border-b py-1 flex flex-col gap-1 text-xs"
                >
                  <span>
                    <b>{d.id}</b> ({d.status})
                  </span>
                  <span>Location: {getNodeName(d.location)}</span>
                  {d.finalDestination && (
                    <span>Destination: {getNodeName(d.finalDestination)}</span>
                  )}
                  {d.passengers.length > 0 && (
                    <span>
                      Riders: {d.passengers.map((p) => p.userId).join(", ")}
                    </span>
                  )}
                  {d.status === "en-route" && (
                    <button
                      onClick={() => handleComplete(d.id)}
                      className="bg-green-600 text-white text-xs rounded py-1 mt-1"
                    >
                      Complete Ride
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Map Panel */}
        <div className="col-span-2 bg-white border rounded-md shadow-sm flex items-center justify-center relative">
          <SimpleMap
  graphData={graphData}
  currentRoute={currentRoute}
  selectedSource={selectedSource}
  selectedDest={selectedDest}
  onNodeClick={handleNodeClick}
  drivers={drivers} // ✅ added this
/>

        </div>
      </div>
    </div>
  );
}

// -----------------------
// Simple Map Component
// -----------------------
function SimpleMap({
  graphData,
  currentRoute,
  selectedSource,
  selectedDest,
  onNodeClick,
  drivers,
}: {
  graphData: GraphData;
  currentRoute: Route | null;
  selectedSource: string | null;
  selectedDest: string | null;
  onNodeClick: (id: string) => void;
  drivers: Driver[];
}) {
  const width = 961 ;
  const height = 635;
  const padding = 60;

  if (graphData.nodes.length === 0)
    return <div className="text-gray-500">Loading map...</div>;

  // --- Normalize coordinates symmetrically ---
  const lats = graphData.nodes.map((n) => n.lat);
  const lngs = graphData.nodes.map((n) => n.lng);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLng = Math.min(...lngs);
  const maxLng = Math.max(...lngs);

  const latRange = maxLat - minLat;
  const lngRange = maxLng - minLng;
  const aspectRatio = width / height;
  const adjustedRange = Math.max(latRange, lngRange / aspectRatio);

  const latToY = (lat: number) =>
    height -
    padding -
    ((lat - minLat) / adjustedRange) * (height - 2 * padding);
  const lngToX = (lng: number) =>
    padding + ((lng - minLng) / adjustedRange) * (width - 2 * padding);

  const getNode = (id: string) => graphData.nodes.find((n) => n.id === id);

  return (
    <svg width={width} height={height} className="bg-gray-100 rounded-md">
      {/* --- Edges + Weights --- */}
      {graphData.edges.map((e, i) => {
        const n1 = getNode(e.u);
        const n2 = getNode(e.v);
        if (!n1 || !n2) return null;
        const x1 = lngToX(n1.lng);
        const y1 = latToY(n1.lat);
        const x2 = lngToX(n2.lng);
        const y2 = latToY(n2.lat);
        const midX = (x1 + x2) / 2;
        const midY = (y1 + y2) / 2;

        return (
          <g key={i}>
            <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#cbd5e1" strokeWidth="2" />
            {/* Edge weight */}
            <text
              x={midX}
              y={midY - 4}
              textAnchor="middle"
              fontSize="10"
              fill="#4b5563"
              className="select-none"
            >
              {e.weight.toFixed(1)}
            </text>
          </g>
        );
      })}

      {/* --- Highlight route if active --- */}
      {currentRoute &&
        currentRoute.path?.length > 1 &&
        currentRoute.path.slice(0, -1).map((id, i) => {
          const n1 = getNode(id);
          const n2 = getNode(currentRoute.path[i + 1]);
          if (!n1 || !n2) return null;
          return (
            <line
              key={i}
              x1={lngToX(n1.lng)}
              y1={latToY(n1.lat)}
              x2={lngToX(n2.lng)}
              y2={latToY(n2.lat)}
              stroke="#2563eb"
              strokeWidth="4"
            />
          );
        })}

      {/* --- Nodes --- */}
      {graphData.nodes.map((n) => {
        const isSrc = selectedSource === n.id;
        const isDst = selectedDest === n.id;
        const fill = isSrc ? "#16a34a" : isDst ? "#dc2626" : "#6b7280";
        return (
          <g key={n.id}>
            <circle
              cx={lngToX(n.lng)}
              cy={latToY(n.lat)}
              r={8}
              fill={fill}
              stroke="white"
              onClick={() => onNodeClick(n.id)}
              className="cursor-pointer"
            />
            <text
              x={lngToX(n.lng)}
              y={latToY(n.lat) - 12}
              textAnchor="middle"
              fontSize="11"
              fill="#111827"
            >
              {n.id}
            </text>
          </g>
        );
      })}

      {/* --- Drivers --- */}
      {drivers.map((d, i) => {
        const node = getNode(d.location);
        if (!node) return null;
        return (
          <g key={i}>
            <circle
              cx={lngToX(node.lng)}
              cy={latToY(node.lat) + 10}
              r={5}
              fill="#1e3a8a"
              stroke="white"
            />
            <text
              x={lngToX(node.lng)}
              y={latToY(node.lat) + 22}
              textAnchor="middle"
              fontSize="10"
              fill="#1e3a8a"
            >
              {d.id.replace("Driver-", "D")}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

