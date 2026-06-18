<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/RatisUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/RatisUtil.java

## Purpose

`RatisUtil` builds and configures Ratis properties for SCM HA and maps low-level Ratis/security exceptions into service exceptions with the correct retry/failover semantics.

## Important APIs, Types, and Functions

Important APIs are `newRaftProperties`, `setRaftStorageDir`, and `checkRatisException`. Private helpers configure RPC, leader election, log, retry cache, and snapshots. It defines behavior for `NonRetriableException`, `RetriableWithNoFailoverException`, `RetriableWithFailOverException`, and converted not-leader exceptions.

## Control Flow

`newRaftProperties` creates properties, sets storage directory, log settings, RPC settings, retry cache, snapshot settings, leader-election settings, and applies raw overrides matching the SCM HA Ratis prefix. `checkRatisException` examines IOException causes through `SCMHAUtils`, converts not-leader responses with peer endpoint metadata, and maps selected SCM security error codes to retry categories.

## State and Persistence Behavior

The utility owns no state. It points Ratis at the configured SCM Ratis storage directory and influences Ratis log/snapshot persistence through returned properties.

## Dependencies and Integration Points

It integrates with `ScmConfigKeys`, `SCMHAUtils`, Ratis server config keys, `RatisHelper`, gRPC config, SCM Ratis server peer ID conversion, and SCM security exception codes.

## Risks and Edge Cases

Ratis request timeout must exceed 1000 ms or configuration fails. Log appender buffer byte limit is cast to int. Raw prefixed overrides can override earlier settings. Security exception mapping is selective; unmapped security errors fall through without throwing.

## Test Signals

Tests should assert property values for storage, RPC type/port/timeouts, log sizes and purge settings, retry cache, snapshots, pre-vote, prefixed overrides, invalid timeout rejection, and exception mapping for not-leader, non-retriable, no-failover retry, failover retry, and certificate failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/RatisUtil.java -->
