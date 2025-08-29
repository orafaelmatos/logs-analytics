import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { useToast } from "@/hooks/use-toast";
import { registerLog, useServices } from "@/hooks/useLogAPI";
import { ArrowLeft, Send } from "lucide-react";


interface Log {
  id: string;
  service: string;
  level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";
  message: string;
}

const logSchema = z.object({
  service: z.string().min(1, "Service is required"),
  level: z.enum(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], {
    required_error: "Log level is required",
  }),
  message: z.string().min(1, "Message is required"),
});

type LogFormData = z.infer<typeof logSchema>;

const LOG_LEVELS = [
  { value: "DEBUG", label: "Debug", color: "text-muted-foreground" },
  { value: "INFO", label: "Info", color: "text-info" },
  { value: "WARNING", label: "Warning", color: "text-warning" },
  { value: "ERROR", label: "Error", color: "text-error" },
  { value: "CRITICAL", label: "Critical", color: "text-critical" },
];

export default function RegisterLog() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const { data: services = [] } = useServices();
  const [customService, setCustomService] = useState("");
  const [useCustomService, setUseCustomService] = useState(false);

  const form = useForm<LogFormData>({
    resolver: zodResolver(logSchema),
    defaultValues: {
      service: "",
      level: "INFO",
      message: "",
    },
  });

  const registerLogMutation = useMutation({
    mutationFn: registerLog,
    onSuccess: (newLog) => {
      toast({
        title: "Log registered successfully",
        description: "Your log entry has been recorded.",
      });

      queryClient.setQueryData<Log[]>(['logs'], (oldData) => {
        if (!oldData) return [newLog];
        return [newLog, ...oldData];
      });

      queryClient.invalidateQueries({ queryKey: ["metrics"] });
      queryClient.invalidateQueries({ queryKey: ["services"] });

      // Reset form
      form.reset();

      // Navigate back to dashboard
      navigate("/");
    },
    onError: (error: Error) => {
      toast({
        title: "Error registering log",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  const onSubmit = (data: LogFormData) => {
    const serviceValue = useCustomService ? customService : data.service;

    registerLogMutation.mutate({
      service: serviceValue,
      level: data.level,
      message: data.message,
    });
  };

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="mx-auto max-w-2xl space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate("/")} className="shrink-0">
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">Register Log</h1>
            <p className="text-muted-foreground">Submit a new log entry to the monitoring system</p>
          </div>
        </div>

        {/* Registration Form */}
        <Card className="border-accent">
          <CardHeader>
            <CardTitle className="text-xl">Log Details</CardTitle>
            <CardDescription>Fill out the form below to register a new log entry</CardDescription>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                {/* Service Selection */}
                <div className="space-y-3">
                  <Label className="text-sm font-medium">Service</Label>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <input
                        type="radio"
                        id="existing-service"
                        name="service-type"
                        checked={!useCustomService}
                        onChange={() => setUseCustomService(false)}
                        className="accent-primary"
                      />
                      <Label htmlFor="existing-service" className="text-sm">
                        Select existing service
                      </Label>
                    </div>

                    {!useCustomService && (
                      <FormField
                        control={form.control}
                        name="service"
                        render={({ field }) => (
                          <FormItem>
                            <FormControl>
                              <Select onValueChange={field.onChange} value={field.value}>
                                <SelectTrigger className="bg-card border-accent">
                                  <SelectValue placeholder="Choose a service" />
                                </SelectTrigger>
                                <SelectContent>
                                  {services.map((service) => (
                                    <SelectItem key={service} value={service}>
                                      {service}
                                    </SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            </FormControl>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    )}

                    <div className="flex items-center gap-2">
                      <input
                        type="radio"
                        id="custom-service"
                        name="service-type"
                        checked={useCustomService}
                        onChange={() => setUseCustomService(true)}
                        className="accent-primary"
                      />
                      <Label htmlFor="custom-service" className="text-sm">
                        Create new service
                      </Label>
                    </div>

                    {useCustomService && (
                      <div>
                        <Input
                          placeholder="Enter service name"
                          value={customService}
                          onChange={(e) => {
                            setCustomService(e.target.value);
                            form.setValue("service", e.target.value);
                          }}
                          className="bg-card border-accent"
                        />
                        {!customService && <p className="text-sm text-destructive mt-1">Service name is required</p>}
                      </div>
                    )}
                  </div>
                </div>

                {/* Log Level */}
                <FormField
                  control={form.control}
                  name="level"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Log Level</FormLabel>
                      <FormControl>
                        <Select onValueChange={field.onChange} value={field.value}>
                          <SelectTrigger className="bg-card border-accent">
                            <SelectValue placeholder="Select log level" />
                          </SelectTrigger>
                          <SelectContent>
                            {LOG_LEVELS.map((level) => (
                              <SelectItem key={level.value} value={level.value}>
                                <span className={level.color}>{level.label}</span>
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Message */}
                <FormField
                  control={form.control}
                  name="message"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Message</FormLabel>
                      <FormControl>
                        <Textarea
                          placeholder="Enter log message..."
                          className="bg-card border-accent min-h-[120px] resize-none"
                          {...field}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Submit Button */}
                <div className="flex gap-4 pt-4">
                  <Button type="submit" disabled={registerLogMutation.isPending} className="flex-1">
                    {registerLogMutation.isPending ? (
                      "Registering..."
                    ) : (
                      <>
                        <Send className="mr-2 h-4 w-4" />
                        Register Log
                      </>
                    )}
                  </Button>
                  <Button type="button" variant="outline" onClick={() => navigate("/")}>
                    Cancel
                  </Button>
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
