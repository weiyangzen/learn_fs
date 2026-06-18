# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/TestDiskBalancerProtocolServer.java

## Purpose
Unit tests for `DiskBalancerProtocolServer` operations: info/status reporting, start, stop, configuration update, and admin privilege enforcement.

## Important APIs, Types, And Functions
Uses `getDiskBalancerInfo`, `startDiskBalancer`, `stopDiskBalancer`, `updateDiskBalancerConfiguration`, `DiskBalancerInfo`, `PrivilegedOperation`, and disk balancer protobufs.

## Control Flow
Setup mocks datanode state, container, service, disk balancer info, datanode details, and admin checkers. Tests compare report fields, mutate running/config state through operations, verify service refreshes, and assert denied operations throw.

## State And Persistence
State is in-memory `DiskBalancerInfo`. No YAML persistence is exercised.

## Dependencies And Integration Points
Integrates datanode identity, Ozone container disk balancer service, HDDS protobufs, and admin authorization hooks.

## Risks And Edge Cases
Uses an old client-version request constant, indirectly covering compatibility. Exact denial messages are asserted.

## Test Signals
Field-by-field protobuf equality, running status changes, refresh counts, and admin-denial exceptions validate behavior.
