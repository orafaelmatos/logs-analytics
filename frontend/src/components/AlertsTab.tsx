import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertTriangle, CheckCircle, Clock, TrendingUp } from "lucide-react";
import { AlertData } from "@/hooks/useLogAPI";
import { cn } from "@/lib/utils";

interface AlertsTabProps {
  alerts: AlertData[];
  isLoading: boolean;
}

const getAlertSeverity = (count: number, threshold: number) => {
  const ratio = count / threshold;
  if (ratio >= 2) return 'critical';
  if (ratio >= 1.5) return 'high';
  if (ratio >= 1) return 'medium';
  return 'low';
};

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case 'critical':
      return 'bg-destructive/20 text-destructive border-destructive/30';
    case 'high':
      return 'bg-error/20 text-error border-error/30';
    case 'medium':
      return 'bg-warning/20 text-warning border-warning/30';
    case 'low':
      return 'bg-success/20 text-success border-success/30';
    default:
      return 'bg-muted/20 text-muted-foreground border-muted/30';
  }
};

const AlertsTab = ({ alerts, isLoading }: AlertsTabProps) => {
  const activeAlerts = alerts.filter(alert => alert.active);
  const resolvedAlerts = alerts.filter(alert => !alert.active);

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="shadow-card border-border">
            <CardContent className="pt-6">
              <div className="animate-pulse space-y-3">
                <div className="h-6 bg-muted rounded w-1/2" />
                <div className="h-4 bg-muted rounded w-3/4" />
                <div className="h-4 bg-muted rounded w-1/4" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Active Alerts */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-destructive" />
          Active Alerts ({activeAlerts.length})
        </h3>
        
        {activeAlerts.length === 0 ? (
          <Alert className="border-success/30 bg-success/10">
            <CheckCircle className="h-4 w-4 text-success" />
            <AlertDescription className="text-success">
              No active alerts. All systems are operating normally.
            </AlertDescription>
          </Alert>
        ) : (
          <div className="space-y-4">
            {activeAlerts.map((alert) => {
              const severity = getAlertSeverity(alert.count, alert.threshold);
              const severityColor = getSeverityColor(severity);
              
              return (
                <Card 
                  key={alert.id} 
                  className={cn(
                    "shadow-card border-2 transition-all duration-300",
                    severity === 'critical' && "border-destructive/50 shadow-glow",
                    severity === 'high' && "border-error/50",
                    severity === 'medium' && "border-warning/50",
                    severity === 'low' && "border-border"
                  )}
                >
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-destructive" />
                        <span>{alert.service}</span>
                      </div>
                      <Badge className={cn("capitalize", severityColor)}>
                        {severity}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                          Level: <span className="capitalize font-medium">{alert.level}</span>
                        </span>
                        <div className="flex items-center gap-2">
                          <TrendingUp className="h-4 w-4 text-destructive" />
                          <span className="font-mono font-bold">
                            {alert.count} / {alert.threshold}
                          </span>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        <span className="font-mono">
                          {new Date(alert.timestamp).toLocaleString()}
                        </span>
                      </div>
                      
                      <div className="text-sm">
                        <span className="text-muted-foreground">Threshold exceeded by: </span>
                        <span className="font-bold text-destructive">
                          {((alert.count / alert.threshold - 1) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Recent Resolved Alerts */}
      {resolvedAlerts.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-success" />
            Recently Resolved ({resolvedAlerts.length})
          </h3>
          
          <div className="space-y-3">
            {resolvedAlerts.slice(0, 5).map((alert) => (
              <Card key={alert.id} className="shadow-card border-border opacity-60">
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-success" />
                      <span className="font-medium">{alert.service}</span>
                      <Badge variant="secondary" className="capitalize">
                        {alert.level}
                      </Badge>
                    </div>
                    <span className="text-sm text-muted-foreground font-mono">
                      {new Date(alert.timestamp).toLocaleString()}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AlertsTab;