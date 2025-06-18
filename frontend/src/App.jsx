import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import DashboardLayout from "./layouts/DashboardLayout";
import Compare from "./pages/Compare";
import Home from "./pages/home";
import Insights from "./pages/Insights";
import SearchResults from "./pages/SearchResults";
import Sentiment from "./pages/Sentiment";
function App() {
  return (
    <Router>
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/search/:symbol" element={<SearchResults />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/sentiment" element={<Sentiment />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;