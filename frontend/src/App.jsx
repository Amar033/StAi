import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Home from './pages/Home';
import SearchResults from './pages/SearchResults';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/search/:symbol" element={<SearchResults />} />
      </Routes>
    </Router>
  );
}

export default App;
