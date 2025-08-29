import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

interface MetricCardProps {
  title: string;
  value: number;
  change?: number;
  variant: 'info' | 'warning' | 'error' | 'success' | 'debug';
  icon?: React.ReactNode;
}

const variantStyles = {
  info: "bg-gradient-primary border-info/30",
  warning: "bg-gradient-warning border-warning/30", 
  error: "bg-gradient-error border-error/30",
  debug: "bg-gradient-base border-white/30",
  success: "bg-gradient-success border-success/30"
};

const MetricCard = ({ title, value, change, variant, icon }: MetricCardProps) => {
  const isPositiveChange = change && change > 0;
  const isNegativeChange = change && change < 0;

  return (
    <Card className={cn(
      "relative overflow-hidden border shadow-card transition-all duration-300 hover:shadow-glow",
      variantStyles[variant]
    )}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-card-foreground/80">
          {title}
        </CardTitle>
        {icon || <Activity className="h-4 w-4 text-card-foreground/60" />}
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline space-x-2">
          <div className="text-2xl font-bold text-card-foreground">
            {value.toLocaleString()}
          </div>
          {change !== undefined && (
            <Badge 
              variant="secondary" 
              className={cn(
                "text-xs flex items-center space-x-1",
                isPositiveChange && "bg-success/20 text-success border-success/30",
                isNegativeChange && "bg-destructive/20 text-destructive border-destructive/30"
              )}
            >
              {isPositiveChange && <TrendingUp className="h-3 w-3" />}
              {isNegativeChange && <TrendingDown className="h-3 w-3" />}
              <span>{Math.abs(change)}%</span>
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default MetricCard;