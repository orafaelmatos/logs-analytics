import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { X } from "lucide-react";

interface FilterControlsProps {
  services: string[];
  selectedService?: string;
  selectedLevel?: string;
  onServiceChange: (service?: string) => void;
  onLevelChange: (level?: string) => void;
}

const LOG_LEVELS = ['ERROR', 'WARNING', 'INFO', 'DEBUG'];

const FilterControls = ({ 
  services, 
  selectedService, 
  selectedLevel, 
  onServiceChange, 
  onLevelChange 
}: FilterControlsProps) => {
  return (
    <Card className="shadow-card border-border">
      <CardContent className="pt-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label className="text-sm font-medium text-muted-foreground mb-2 block">
              Filter by Service
            </label>
            <Select 
              value={selectedService || "all"} 
              onValueChange={(value) => onServiceChange(value === "all" ? undefined : value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Services" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Services</SelectItem>
                {services.map((service) => (
                  <SelectItem key={service} value={service}>
                    {service}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex-1">
            <label className="text-sm font-medium text-muted-foreground mb-2 block">
              Filter by Level
            </label>
            <Select 
              value={selectedLevel || "all"} 
              onValueChange={(value) => onLevelChange(value === "all" ? undefined : value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="All Levels" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Levels</SelectItem>
                {LOG_LEVELS.map((level) => (
                  <SelectItem key={level} value={level}>
                    <span className="capitalize">{level}</span>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {(selectedService || selectedLevel) && (
          <div className="flex gap-2 mt-4">
            {selectedService && (
              <Badge variant="secondary" className="flex items-center gap-2">
                Service: {selectedService}
                <X 
                  className="h-3 w-3 cursor-pointer" 
                  onClick={() => onServiceChange(undefined)}
                />
              </Badge>
            )}
            {selectedLevel && (
              <Badge variant="secondary" className="flex items-center gap-2">
                Level: {selectedLevel}
                <X 
                  className="h-3 w-3 cursor-pointer" 
                  onClick={() => onLevelChange(undefined)}
                />
              </Badge>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default FilterControls;