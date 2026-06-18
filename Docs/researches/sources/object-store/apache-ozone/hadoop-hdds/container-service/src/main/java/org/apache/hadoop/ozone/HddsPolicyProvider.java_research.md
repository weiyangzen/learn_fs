# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsPolicyProvider.java

## Purpose
Hadoop service authorization policy provider for datanode RPC protocols.

## Important APIs, Types, And Functions
Singleton `getInstance()` is backed by Ratis `MemoizedSupplier`. `getServices()` returns ACL mappings for reconfiguration and disk balancer protocols.

## Control Flow
When client RPC server starts under Hadoop service authorization, it refreshes service ACLs using this provider.

## State And Persistence
State is a memoized singleton and static immutable list of `Service` mappings.

## Dependencies And Integration Points
Depends on Hadoop `PolicyProvider`, HDDS ACL config keys, `ReconfigureProtocol`, `DiskBalancerProtocol`, and Ratis memoized supplier.

## Risks
Adding new datanode RPC protocols requires updating this provider or ACLs will not apply. Returned array is a copy, but service objects are shared.

## Test Signals
Signals include ACL refresh, authorized/unauthorized RPC behavior for reconfigure and disk balancer, and singleton reuse.
