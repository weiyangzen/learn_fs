# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerUpdateSubcommand.java

## Purpose
Implements `ozone admin datanode diskbalancer update`, changing DiskBalancer configuration on selected datanodes.

## Important APIs, Types, And Functions
Options mirror start: threshold, bandwidth, parallel thread, stop-after-even, and container states. `validateParameters` requires at least one option. `buildConfigProto` creates `HddsProtos.DiskBalancerConfigurationProto`; `executeCommand` calls `updateDiskBalancerConfiguration`.

## Control Flow
After base validation, each datanode receives a config proto containing only fields supplied by the user. The command returns JSON success maps or prints consolidated text summaries.

## State And Persistence
It mutates datanode-local DiskBalancer configuration.

## Dependencies And Integration Points
Depends on `DiskBalancerProtocol.updateDiskBalancerConfiguration`, protobuf config, and base DiskBalancer target handling.

## Risks And Test Signals
Input range and container state validation are left to server-side logic. Tests should cover no options error, each option's inclusion, partial node failures, JSON configuration maps, batch mode, and proxy close on exceptions.
