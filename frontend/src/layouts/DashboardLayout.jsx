import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";

const DashboardLayout = () => {
  return (
    <div className="min-h-screen bg-background-950 text-text-50">
      <Sidebar />
      <main className="md:ml-64 p-6 overflow-y-auto min-h-screen">
        <Outlet />
      </main>
    </div>
  );
};

export default DashboardLayout;