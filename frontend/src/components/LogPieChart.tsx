import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TooltipProps } from "recharts";

interface LogData {
  level: string;
  count: number;
}

interface LogPieChartProps {
  data: LogData[];
}

const COLORS = {
  ERROR: "#ef4444",
  WARNING: "#f59e0b",
  INFO: "#3b82f6",
  DEBUG: "#6b7280",
  SUCCESS: "#10b981",
};

const CustomTooltip = ({ active, payload }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    const { level, count, fill } = payload[0].payload;
    return (
      <div
        style={{
          backgroundColor: "#fff",
          padding: "8px 12px",
          borderRadius: "8px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.15)",
          color: "#333",
          minWidth: "120px",
          fontSize: "0.9rem",
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
          <strong>{level}</strong>
        </div>
        <div style={{ marginTop: "4px" }}>Count: {count}</div>
      </div>
    );
  }

  return null;
};

const LogPieChart = ({ data }: LogPieChartProps) => {
  const chartData = data.map((item) => ({
    ...item,
    fill: COLORS[item.level as keyof typeof COLORS] || "hsl(var(--chart-1))",
  }));

  return (
    <Card className="shadow-card border-border">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">Logs by Level</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie data={chartData} cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={2} dataKey="count" nameKey="level" label>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
};

export default LogPieChart;
