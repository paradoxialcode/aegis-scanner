import { OpenPort } from '@/lib/data';

export default function PortsTable({ ports }: { ports: OpenPort[] }) {
  return (
    <div className="bg-dashboard-card rounded-xl border border-gray-800 overflow-hidden mb-8">
      <div className="p-6 border-b border-gray-800">
        <h3 className="text-white font-semibold">Open Ports</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-800/30 text-gray-400 text-xs uppercase tracking-wider">
              <th className="p-4 font-medium">Port</th>
              <th className="p-4 font-medium">Protocol</th>
              <th className="p-4 font-medium">Service</th>
              <th className="p-4 font-medium">State</th>
            </tr>
          </thead>
          <tbody className="text-sm divide-y divide-gray-800">
            {ports.map((port, index) => (
              <tr key={index} className="hover:bg-gray-800/20 transition-colors">
                <td className="p-4 text-white font-medium">{port.port}</td>
                <td className="p-4 text-gray-300 uppercase">{port.protocol}</td>
                <td className="p-4 text-gray-300">{port.service}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    port.state === 'open' ? 'bg-severity-low/20 text-severity-low' : 
                    port.state === 'filtered' ? 'bg-severity-medium/20 text-severity-medium' : 
                    'bg-gray-700 text-gray-300'
                  }`}>
                    {port.state}
                  </span>
                </td>
              </tr>
            ))}
            {ports.length === 0 && (
              <tr>
                <td colSpan={4} className="p-8 text-center text-gray-500">
                  No open ports found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
