export default function Header() {
  return (
    <header className="h-20 flex items-center pl-16 pr-8 bg-dashboard-bg border-b border-gray-800">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-sm text-gray-400">Latest scan overview</p>
      </div>
    </header>
  );
}