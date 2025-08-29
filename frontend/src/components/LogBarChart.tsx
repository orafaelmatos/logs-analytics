import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, TooltipProps } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ServiceData {
  service: string;
  count: number;
}

interface LogBarChartProps {
  data: ServiceData[];
}

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#6b7280"];

const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    const { service, count, fill } = payload[0].payload;
    return (
      <div
        style={{
          backgroundColor: "#fff",
          padding: "8px 12px",
          borderRadius: "8px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
          color: "#333",
          fontSize: "0.9rem",
          minWidth: "140px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <div
            style={{
              width: "12px",
              height: "12px",
              borderRadius: "50%",
              backgroundColor: fill,
            }}
          ></div>
          <strong>{service}</strong>
        </div>
        <div style={{ marginTop: "4px" }}>Count: {count}</div>
      </div>
    );
  }
  return null;
};

const LogBarChart = ({ data }: LogBarChartProps) => {
  return (
    <Card className="shadow-card border-border">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Logs by Service</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={data}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="service" stroke="#6b7280" fontSize={12} />
            <YAxis stroke="#6b7280" fontSize={12} />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey="count"
              radius={[6, 6, 0, 0]}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default LogBarChart;
