# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerStartSubcommand.java

## Purpose
Implements `ozone admin datanode diskbalancer start`, starting DiskBalancer on selected datanodes with optional configuration overrides.

## Important APIs, Types, And Functions
Options include `--threshold-percentage`, `--bandwidth-in-mb`, `--parallel-thread`, `--stop-after-disk-even`, and `--container-states`. `buildConfigProto` creates `DiskBalancerConfigurationProto`; `executeCommand` calls `startDiskBalancer`.

## Control Flow
The abstract base validates targets and feature flag. For each datanode, this command opens a proxy, builds a config containing only supplied fields, starts DiskBalancer, returns a success JSON map, and closes the proxy. Text mode summarizes success/failure by batch or explicit target mode.

## State And Persistence
It mutates datanode-local DiskBalancer service state and configuration.

## Dependencies And Integration Points
Depends on `DiskBalancerProtocol.startDiskBalancer`, protobuf configuration, and shared display/config map helpers.

## Risks And Test Signals
There is no local validation for negative threshold, bandwidth, or threads, nor enum validation for `containerStates`. Tests should cover each config field, invalid values as handled by server, JSON success/error shape, batch success message, and proxy close on failure.
