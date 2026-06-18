# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/MaintenanceSubCommand.java

## Purpose
Implements `ozone admin datanode maintenance`, starting maintenance mode on one or more datanodes.

## Important APIs, Types, And Functions
The command extends `ScmSubcommand`, mixes in `HostNameParameters`, supports `--end` hours and `--force`, and calls `ScmClient.startMaintenanceNodes(hosts, endInHours, force)`.

## Control Flow
It sends the maintenance request for all hosts, prints the requested hosts, then delegates partial-failure handling to `DecommissionSubCommand.showErrors`.

## State And Persistence
It mutates SCM datanode operational state and may set a maintenance expiry timestamp.

## Dependencies And Integration Points
Depends on SCM datanode admin APIs and shared host/error handling.

## Risks And Test Signals
`--force` description mentions decommission instead of maintenance. There is no local validation for negative `--end`. Tests should cover expiry propagation, force flag, partial failures, and non-zero exit on errors.
