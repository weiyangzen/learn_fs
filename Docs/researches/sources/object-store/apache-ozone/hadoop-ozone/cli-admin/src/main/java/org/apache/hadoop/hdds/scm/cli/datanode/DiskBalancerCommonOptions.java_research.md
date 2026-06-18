# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerCommonOptions.java

## Purpose
Defines common options shared by all DiskBalancer datanode subcommands.

## Important APIs, Types, And Functions
It mixes in `DatanodeParameters`, exposes `--in-service-datanodes` and `--json`, and provides getters `getDatanodes`, `isInServiceDatanodes`, and `isJson`.

## Control Flow
Picocli populates the mixin before `AbstractDiskBalancerSubCommand.call()` reads it. `getDatanodes` returns an empty list when no positional mixin data is present, supporting batch mode without addresses.

## State And Persistence
Holds invocation options only.

## Dependencies And Integration Points
Used by all DiskBalancer subcommands through the abstract base class.

## Risks And Test Signals
Combining explicit datanodes with `--in-service-datanodes` is not rejected here; the base class chooses batch mode. Tests should cover JSON flag propagation, absent positional args, and mixed selection behavior.
