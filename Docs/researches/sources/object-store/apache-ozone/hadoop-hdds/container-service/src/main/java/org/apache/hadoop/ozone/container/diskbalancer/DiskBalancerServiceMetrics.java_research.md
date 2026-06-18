# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerServiceMetrics.java

Purpose: Singleton Metrics2 source for disk balancer service activity.

Important APIs and types: Static `create` registers the singleton, `unRegister` removes it. Counters track successful jobs, successfully moved bytes, failed jobs, running loops, idle loops with no volume pair, and idle loops due to bandwidth. Mutable rates track successful and failed move durations.

Control flow: `DiskBalancerService` increments counters throughout scheduling and task completion. `toString` reports current counter values and mean move times.

State and persistence: Runtime metrics only; no durable state. Static singleton `instance` is reset on unregister.

Dependencies and integration points: Uses Hadoop Metrics2 default system. `DiskBalancerService.getDiskBalancerInfo` reads success/failure counters and bytes to populate reports.

Risks: `create` is not synchronized, so concurrent service construction could race registration. `unRegister` unregisters regardless of whether the source is registered. Tests should cover singleton behavior, counter increments, rate updates from task completion, and unregister/recreate lifecycle.
