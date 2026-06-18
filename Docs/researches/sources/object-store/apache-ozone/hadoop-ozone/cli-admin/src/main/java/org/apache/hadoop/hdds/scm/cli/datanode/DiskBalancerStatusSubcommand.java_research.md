# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/datanode/DiskBalancerStatusSubcommand.java

## Purpose
Implements `ozone admin datanode diskbalancer status`, showing current DiskBalancer status, configuration, move counts, and estimated remaining work.

## Important APIs, Types, And Functions
Extends `AbstractDiskBalancerSubCommand`; calls `DiskBalancerProtocol.getDiskBalancerInfo`; `generateStatus` renders tabular status; `createStatusResult` builds JSON; `calculateEstimatedTimeLeft` derives minutes from bytes-to-move and configured MB/s.

## Control Flow
Each target is queried via a datanode proxy. JSON mode returns one map per datanode to the base class; text mode stores protos and later prints a consolidated table plus explanatory notes.

## State And Persistence
Read-only against datanode DiskBalancer state. Local cached status map is transient.

## Dependencies And Integration Points
Depends on `DatanodeDiskBalancerInfoProto`, `DiskBalancerConfigurationProto`, and `DiskBalancerSubCommandUtil`.

## Risks And Test Signals
It assumes `getDiskBalancerConf()` exists and divides by bandwidth, returning N/A when bandwidth is zero. Tests should cover zero bytes remaining, zero bandwidth, absent container states, failed node errors, JSON null estimate, and table formatting.
