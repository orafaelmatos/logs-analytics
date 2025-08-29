import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { BarChart3, TrendingUp } from "lucide-react";
import { MetricData } from "@/hooks/useLogAPI";
import { cn } from "@/lib/utils";

interface MetricsTabProps {
  metrics: MetricData[];
  isLoading: boolean;
}

const getLevelColor = (level: string) => {
  switch (level.toLowerCase()) {
    case 'error':
      return 'bg-error/20 text-error border-error/30';
    case 'warning':
      return 'bg-warning/20 text-warning border-warning/30';
    case 'info':
      return 'bg-info/20 text-info border-info/30';
    case 'debug':
      return 'bg-debug/20 text-debug border-debug/30';
    default:
      return 'bg-muted/20 text-muted-foreground border-muted/30';
  }
};

const MetricsTab = ({ metrics, isLoading }: MetricsTabProps) => {
  // Group metrics by service
  const groupedMetrics = metrics.reduce((acc, metric) => {
    if (!acc[metric.service]) {
      acc[metric.service] = [];
    }
    acc[metric.service].push(metric);
    return acc;
  }, {} as Record<string, MetricData[]>);

  if (isLoading) {
    return (
      <div className="space-y-6">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="shadow-card border-border">
            <CardContent className="pt-6">
              <div className="animate-pulse space-y-4">
                <div className="h-6 bg-muted rounded w-1/3" />
                <div className="h-32 bg-muted rounded" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {Object.entries(groupedMetrics).map(([service, serviceMetrics]) => {
        const totalCount = serviceMetrics.reduce((sum, metric) => sum + metric.count, 0);
        
        return (
          <Card key={service} className="shadow-card border-border">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  {service}
                </div>
                <Badge variant="secondary" className="flex items-center gap-2">
                  <TrendingUp className="h-3 w-3" />
                  Total: {totalCount.toLocaleString()}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border border-border overflow-hidden">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-muted/50">
                      <TableHead>Level</TableHead>
                      <TableHead className="text-right">Count</TableHead>
                      <TableHead>Timestamp</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {serviceMetrics.map((metric, index) => (
                      <TableRow key={index} className="hover:bg-muted/30 transition-colors">
                        <TableCell>
                          <Badge 
                            className={cn(
                              "w-fit capitalize",
                              getLevelColor(metric.level)
                            )}
                          >
                            {metric.level}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right font-mono font-medium">
                          {metric.count.toLocaleString()}
                        </TableCell>
                        <TableCell className="font-mono text-sm text-muted-foreground">
                          {new Date(metric.timestamp).toLocaleString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        );
      })}
      
      {Object.keys(groupedMetrics).length === 0 && (
        <Card className="shadow-card border-border">
          <CardContent className="pt-6">
            <div className="text-center text-muted-foreground py-8">
              No metrics found
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default MetricsTab;