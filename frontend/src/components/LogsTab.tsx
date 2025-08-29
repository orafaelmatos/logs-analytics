import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock, Server, AlertTriangle } from "lucide-react";
import { LogEntry } from "@/hooks/useLogAPI";
import { cn } from "@/lib/utils";

interface LogsTabProps {
  logs: LogEntry[];
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

const getLevelIcon = (level: string) => {
  switch (level.toLowerCase()) {
    case 'error':
      return <AlertTriangle className="h-3 w-3" />;
    case 'warning':
      return <AlertTriangle className="h-3 w-3" />;
    default:
      return <Server className="h-3 w-3" />;
  }
};

const LogsTab = ({ logs, isLoading }: LogsTabProps) => {
  if (isLoading) {
    return (
      <Card className="shadow-card border-border">
        <CardContent className="pt-6">
          <div className="animate-pulse space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-muted rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-card border-border">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Server className="h-5 w-5" />
          Recent Logs
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border border-border overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow className="bg-muted/50">
                <TableHead>Service</TableHead>
                <TableHead>Level</TableHead>
                <TableHead className="text-right">Count</TableHead>
                <TableHead>Timestamp</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {logs.map((log, index) => (
                <TableRow key={index} className="hover:bg-muted/30 transition-colors">
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-2">
                      <Server className="h-4 w-4 text-muted-foreground" />
                      {log.service}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge 
                      className={cn(
                        "flex items-center gap-1 w-fit",
                        getLevelColor(log.level)
                      )}
                    >
                      {getLevelIcon(log.level)}
                      <span className="capitalize">{log.level}</span>
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right font-mono">
                    {log.count.toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Clock className="h-4 w-4" />
                      <span className="font-mono text-sm">
                        {new Date(log.timestamp).toLocaleString()}
                      </span>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {logs.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-muted-foreground py-8">
                    No logs found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
};

export default LogsTab;