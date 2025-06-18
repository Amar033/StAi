import { Activity, BarChart3, DollarSign, LayoutDashboard } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const Sidebar = () => {
  const navItems = [
    { to: "/", icon: LayoutDashboard, label: "Dashboard" },
    // { to: "/search/AAPL", icon: Search, label: "Search" },
    { to: "/insights", icon: DollarSign, label: "Insights" },
    { to: "/compare", icon: BarChart3, label: "Compare" },
    { to: "/sentiment", icon: Activity, label: "Sentiment" }
  ];

  return (
    <aside className="bg-background-950 fixed top-0 left-0 h-screen w-64 p-6 border-r border-background-600/30 hidden md:block z-10">
      <h1 className="text-2xl font-bold text-primary-400 mb-8">StAI</h1>
      <nav className="space-y-3">
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            to={to}
            key={to}
            className={({ isActive }) =>
              `flex items-center gap-3 p-4 rounded-xl transition-all duration-200 ${
                isActive
                  ? "bg-background-800/60 border border-background-600/30 text-primary-400"
                  : "text-text-400 hover:bg-background-800/40 hover:text-text-200 border border-transparent"
              }`
            }
          >
            <Icon className="w-5 h-5" />
            <span className="text-sm font-medium">{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;