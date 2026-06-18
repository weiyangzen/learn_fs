# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeStorageStatMXBean.java

## Purpose
`SCMNodeStorageStatMXBean` defines the JMX management contract for per-datanode and aggregate storage capacity, remaining, used, and volume details.

## Important APIs, Types, And Functions
The interface exposes `getCapacity`, `getRemainingSpace`, `getUsedSpace`, `getTotalCapacity`, `getTotalSpaceUsed`, `getTotalFreeSpace`, and `getStorageVolumes`. Per-node methods use `UUID` datanode IDs and volume details are returned as `Set<StorageLocationReport>`.

## Control Flow
There is no implementation control flow in this file. Implementations are expected to look up a datanode ID, aggregate over its storage reports, and expose totals through JMX.

## State And Persistence Behavior
The interface owns no state. Implementations may back it with in-memory reports derived from datanode node reports, as `SCMNodeStorageStatMap` does.

## Dependencies And Integration Points
It depends on `StorageLocationReport` from the Ozone container common package and Hadoop interface-audience annotations. JMX consumers and SCM storage-stat implementations use this contract.

## Risks And Edge Cases
The contract does not define behavior for unknown datanode IDs, null IDs, empty reports, or whether returned volume sets are defensive copies. Implementers need to document and guard those behaviors.

## Test Signals
Implementation tests should assert per-node and aggregate values, unknown-node behavior, and mutation safety of returned `StorageLocationReport` sets.
