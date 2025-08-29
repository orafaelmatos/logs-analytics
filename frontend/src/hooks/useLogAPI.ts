import { brazilTimeISOString } from "@/lib/time";
import { useQuery } from "@tanstack/react-query";

const API_BASE_URL = "http://localhost:8000"; // Update to your FastAPI backend URL

export interface LogEntry {
  service: string;
  level: string;
  count: number;
  timestamp: string;
}

export interface MetricData {
  service: string;
  level: string;
  count: number;
  timestamp: string;
}

export interface AlertData {
  id: string;
  service: string;
  level: string;
  count: number;
  threshold: number;
  timestamp: string;
  active: boolean;
}

export interface ServiceMetricsResponse {
  service: string;
  metrics: Record<string, number>;
}

// Fetch recent logs
export const useRecentLogs = (limit: number = 50) => {
  return useQuery({
    queryKey: ["logs", "recent", limit],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/logs/recent?limit=${limit}`);
      if (!response.ok) throw new Error("Failed to fetch recent logs");
      return response.json() as Promise<LogEntry[]>;
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  });
};

// Fetch logs by service
export const useLogsByService = (serviceName: string, limit: number = 50) => {
  return useQuery({
    queryKey: ["logs", "service", serviceName, limit],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/logs/service/${serviceName}?limit=${limit}`);
      if (!response.ok) throw new Error("Failed to fetch logs by service");
      return response.json() as Promise<LogEntry[]>;
    },
    enabled: !!serviceName,
    refetchInterval: 10000,
  });
};

// Fetch logs by level
export const useLogsByLevel = (level: string, limit: number = 50) => {
  return useQuery({
    queryKey: ["logs", "level", level, limit],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/logs/level/${level}?limit=${limit}`);
      if (!response.ok) throw new Error("Failed to fetch logs by level");
      return response.json() as Promise<LogEntry[]>;
    },
    enabled: !!level,
    refetchInterval: 10000,
  });
};

// Fetch all services
export const useServices = () => {
  return useQuery({
    queryKey: ["services"],
    queryFn: async () => {
      const response = await fetch(`${API_BASE_URL}/services`);
      if (!response.ok) throw new Error("Failed to fetch services");
      const data = (await response.json()) as { services: string[] };
      return data.services;
    },
  });
};

// Fetch metrics for a service
export const useServiceMetrics = (serviceName: string) => {
  return useQuery<ServiceMetricsResponse>({
    queryKey: ["metrics", "service", serviceName],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/metrics/service/${serviceName}`);
      if (!res.ok) throw new Error("Failed to fetch service metrics");
      return res.json() as Promise<ServiceMetricsResponse>;
    },
    enabled: !!serviceName,
    refetchInterval: 10000,
  });
};

// Fetch all metrics
export const useAllMetrics = () => {
  return useQuery({
    queryKey: ["metrics", "all"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE_URL}/metrics/service/all`);
      if (!res.ok) throw new Error("Failed to fetch all metrics");
      const data: { metrics: Record<string, MetricData[]> } = await res.json();

      // Flatten object into array for the component
      const metricsArray: MetricData[] = [];
      for (const [service, metrics] of Object.entries(data.metrics)) {
        metrics.forEach((metric) => metricsArray.push({ ...metric, service }));
      }
      return metricsArray;
    },
    refetchInterval: 10000,
  });
};

// Fetch alerts
export const useAlerts = (service?: string, level?: string) => {
  return useQuery({
    queryKey: ["alerts", service, level],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (service) params.append("service", service);
      if (level) params.append("level", level);

      const response = await fetch(`${API_BASE_URL}/alerts/?${params.toString()}`);
      if (!response.ok) throw new Error("Failed to fetch alerts");
      return response.json() as Promise<AlertData[]>;
    },
    refetchInterval: 5000, // Refresh alerts more frequently
  });
};

// Register a new log
export const registerLog = async (logData: { service: string; level: string; message: string; timestamp?: string }) => {
  const response = await fetch(`${API_BASE_URL}/logs/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ...logData,
      // send Brazil time as ISO string
      timestamp: logData.timestamp || brazilTimeISOString(),
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to register log");
  }

  return response.json();
};
