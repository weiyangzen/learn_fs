# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DatanodeParameters.java

## Purpose
Provides positional/stdin datanode address parsing for DiskBalancer commands.

## Important APIs, Types, And Functions
`DatanodeParameters` extends `ItemsFromStdin`. `setDatanodes` binds `0..*` `<datanode address>` arguments and documents stdin usage. `getDatanodes` returns a defensive `ArrayList` copy of inherited items.

## Control Flow
Picocli populates items from arguments or stdin marker `-`; consumers retrieve the list through `DiskBalancerCommonOptions`.

## State And Persistence
Input addresses are stored only in memory for the command invocation.

## Dependencies And Integration Points
Used by `DiskBalancerCommonOptions` and all DiskBalancer subcommands.

## Risks And Test Signals
No address validation occurs here; validation/proxy creation is deferred. Tests should cover stdin, empty list with batch mode, host-only addresses, explicit ports, and duplicate preservation before base-class deduplication.
