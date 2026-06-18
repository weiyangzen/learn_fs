# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ReconTaskConfig.java

Purpose: `ReconTaskConfig` defines typed configuration for periodic Recon background tasks and warmup behavior under the `ozone.recon.task` config group.

Important APIs and types: HDDS `@ConfigGroup` and `@Config` annotations define `ozone.recon.task.pipelinesync.interval`, `missingcontainer.interval`, `safemode.wait.threshold`, and `containercounttask.interval`. Values are `Duration` with defaults of 300 seconds for pipeline sync, missing container, and safemode threshold, and 60 seconds for container size count.

Control flow and integration: Recon configuration injection can populate this POJO and task schedulers can read intervals via getters. Setters support tests and explicit programmatic overrides.

State and persistence: in-memory configuration only; durable values come from Ozone configuration files.

Dependencies: HDDS config annotations and Java `Duration`.

Risks and test signals: config key naming is partly redundant with the group prefix, so tests should verify effective key resolution. Duration parsing, default values, and setter/getter round trips should be covered. Operationally, too-small intervals can increase Recon load.
