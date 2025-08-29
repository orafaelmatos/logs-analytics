import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Activity, AlertTriangle, Info, Bug, BarChart3, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import MetricCard from "./MetricCard";
import LogPieChart from "./LogPieChart";
import LogBarChart from "./LogBarChart";
import FilterControls from "./FilterControls";
import LogsTab from "./LogsTab";
import MetricsTab from "./MetricsTab";
import AlertsTab from "./AlertsTab";
import {
  useRecentLogs,
  useLogsByService,
  useLogsByLevel,
  useServices,
  useAllMetrics,
  useAlerts,
  LogEntry,
  MetricData,
  useServiceMetrics,
} from "@/hooks/useLogAPI";
import { info } from "console";

const Dashboard = () => {
  const navigate = useNavigate();
  const [selectedService, setSelectedService] = useState<string>();
  const [selectedLevel, setSelectedLevel] = useState<string>();
  const [activeTab, setActiveTab] = useState("overview");

  // Fetch data
  const { data: recentLogs = [], isLoading: logsLoading } = useRecentLogs(100);
  const { data: serviceFilteredLogs = [] } = useLogsByService(selectedService || "", 50);
  const { data: levelFilteredLogs = [] } = useLogsByLevel(selectedLevel || "", 50);
  const { data: services = [], isLoading: servicesLoading } = useServices();
  const { data: serviceMetricsData, isLoading: metricsLoading } = useServiceMetrics(selectedService || "");
  const { data: alerts = [], isLoading: alertsLoading } = useAlerts(selectedService, selectedLevel);

  // Filter logs based on selected filters
  const filteredLogs = useMemo(() => {
    let logs = recentLogs;

    if (selectedService && selectedLevel) {
      // Use intersection of both filters
      const serviceFiltered = serviceFilteredLogs;
      const levelFiltered = levelFilteredLogs;
      logs = serviceFiltered.filter((log) =>
        levelFiltered.some(
          (levelLog) =>
            levelLog.service === log.service && levelLog.level === log.level && levelLog.timestamp === log.timestamp
        )
      );
    } else if (selectedService) {
      logs = serviceFilteredLogs;
    } else if (selectedLevel) {
      logs = levelFilteredLogs;
    }

    return logs;
  }, [recentLogs, serviceFilteredLogs, levelFilteredLogs, selectedService, selectedLevel]);

  // Calculate metrics for cards
  const metrics = useMemo(() => {
    const logs = selectedService || selectedLevel ? filteredLogs : recentLogs;

    const totalLogs = logs.reduce((sum, log) => sum + log.count, 0);
    const errorLogs = logs.filter((log) => log.level === "ERROR").reduce((sum, log) => sum + log.count, 0);
    const warningLogs = logs.filter((log) => log.level === "WARNING").reduce((sum, log) => sum + log.count, 0);
    const infoLogs = logs.filter((log) => log.level === "INFO").reduce((sum, log) => sum + log.count, 0);
    const debugLogs = logs.filter((log) => log.level === "DEBUG").reduce((sum, log) => sum + log.count, 0);

    return { totalLogs, errorLogs, warningLogs, infoLogs, debugLogs };
  }, [recentLogs, filteredLogs, selectedService, selectedLevel]);

  const transformedMetrics: MetricData[] = useMemo(() => {
    if (!serviceMetricsData) return [];

    const { metrics: metricsObj, service: serviceName } = serviceMetricsData;
    const now = new Date().toISOString();

    return Object.entries(metricsObj).map(([level, count]) => ({
      service: serviceName,
      level,
      count: Number(count),
      timestamp: now,
    }));
  }, [serviceMetricsData]);

  // Prepare chart data
  const pieChartData = useMemo(() => {
    const logs = selectedService || selectedLevel ? filteredLogs : recentLogs;
    const levelCounts = logs.reduce((acc, log) => {
      acc[log.level] = (acc[log.level] || 0) + log.count;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(levelCounts).map(([level, count]) => ({ level, count }));
  }, [recentLogs, filteredLogs, selectedService, selectedLevel]);

  const barChartData = useMemo(() => {
    const logs = selectedService || selectedLevel ? filteredLogs : recentLogs;
    const serviceCounts = logs.reduce((acc, log) => {
      acc[log.service] = (acc[log.service] || 0) + log.count;
      return acc;
    }, {} as Record<string, number>);

    return Object.entries(serviceCounts)
      .map(([service, count]) => ({ service, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10); // Top 10 services
  }, [recentLogs, filteredLogs, selectedService, selectedLevel]);

  const activeAlertCount = alerts.filter((alert) => alert.active).length;

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-primary bg-clip-text text-transparent">
              Log Monitoring Dashboard
            </h1>
            <p className="text-muted-foreground">Real-time monitoring of application logs and metrics</p>
          </div>
          <div className="flex items-center gap-4">
            <Button
              onClick={() => navigate("/register-log")}
              className="bg-gradient-to-r from-primary to-primary-glow hover:from-primary/90 hover:to-primary-glow/90"
            >
              <Plus className="mr-2 h-4 w-4" />
              Register Log
            </Button>
          </div>
        </div>

        {/* Filters */}
        <FilterControls
          services={services}
          selectedService={selectedService}
          selectedLevel={selectedLevel}
          onServiceChange={setSelectedService}
          onLevelChange={setSelectedLevel}
        />

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList
            className={`grid w-full ${selectedService ? "grid-cols-4" : "grid-cols-3"} bg-card border border-border`}
          >
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="logs" className="flex items-center gap-2">
              <Activity className="h-4 w-4" />
              Logs
            </TabsTrigger>

            {selectedService && (
              <TabsTrigger value="metrics" className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Metrics
              </TabsTrigger>
            )}

            <TabsTrigger value="alerts" className="flex items-center gap-2 relative">
              <AlertTriangle className="h-4 w-4" />
              Alerts
              {activeAlertCount > 0 && (
                <span className="absolute -top-1 -right-1 h-4 w-4 bg-destructive text-destructive-foreground text-xs rounded-full flex items-center justify-center">
                  {activeAlertCount}
                </span>
              )}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
              <MetricCard
                title="Total Logs"
                value={metrics.totalLogs}
                variant="success"
                icon={<Activity className="h-4 w-4" />}
              />
              <MetricCard
                title="Errors"
                value={metrics.errorLogs}
                variant="error"
                icon={<AlertTriangle className="h-4 w-4" />}
              />
              <MetricCard
                title="Warnings"
                value={metrics.warningLogs}
                variant="warning"
                icon={<AlertTriangle className="h-4 w-4" />}
              />

              <MetricCard
                title="Info"
                value={metrics.infoLogs}
                variant="info"
                icon={<AlertTriangle className="h-4 w-4" />}
              />

              <MetricCard
                title="Debug"
                value={metrics.debugLogs}
                variant="debug"
                icon={<AlertTriangle className="h-4 w-4" />}
              />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <LogPieChart data={pieChartData} />
              <LogBarChart data={barChartData} />
            </div>
          </TabsContent>

          <TabsContent value="logs">
            <LogsTab logs={filteredLogs} isLoading={logsLoading} />
          </TabsContent>

          <TabsContent value="metrics">
            <MetricsTab metrics={transformedMetrics} isLoading={metricsLoading} />
          </TabsContent>

          <TabsContent value="alerts">
            <AlertsTab alerts={alerts} isLoading={alertsLoading} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Dashboard;
