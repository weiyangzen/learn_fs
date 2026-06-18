# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerCommands.java

## Purpose
Registers the `datanode diskbalancer` command group and documents usage for start, stop, update, report, and status.

## Important APIs, Types, And Functions
`DiskBalancerCommands` is a picocli command with child subcommands `DiskBalancerStartSubcommand`, `DiskBalancerStopSubcommand`, `DiskBalancerUpdateSubcommand`, `DiskBalancerReportSubcommand`, and `DiskBalancerStatusSubcommand`.

## Control Flow
No command execution happens in this class; picocli routes to selected children.

## State And Persistence
No state is held.

## Dependencies And Integration Points
Nested under `DatanodeCommands`; references `HDDS_DATANODE_DISK_BALANCER_ENABLED_KEY` in its description.

## Risks And Test Signals
The large embedded help text can drift from implementation. Tests should verify help output and that each subcommand is reachable.
