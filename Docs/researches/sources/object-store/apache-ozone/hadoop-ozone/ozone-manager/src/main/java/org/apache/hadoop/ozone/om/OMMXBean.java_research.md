# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OMMXBean.java

## Purpose
`OMMXBean` is the JMX management interface for exposing Ozone Manager runtime information. It extends `ServiceRuntimeInfo`, adding OM-specific attributes for RPC, Ratis, RocksDB, and host identity.

## Important APIs, types, and functions
The interface is annotated `@InterfaceAudience.Private` and declares `getRpcPort`, `getRatisRoles`, `getRatisLogDirectory`, `getRocksDbDirectory`, and `getHostname`. `getRatisRoles` returns a nested string list, likely representing per-peer role/status rows, while the directory getters expose local filesystem paths.

## Control flow
There is no implementation or executable control flow in this file. Runtime behavior is supplied by the OM class or another MXBean implementation registered with the metrics/JMX subsystem.

## State and persistence behavior
The interface defines read-only management accessors. It does not persist state and does not prescribe caching. Values are expected to be derived from live OM configuration, service state, and storage layout by implementors.

## Dependencies and integration points
It integrates with Hadoop's `ServiceRuntimeInfo` and Java JMX naming conventions. Monitoring tools and administrators can consume these attributes once the implementing OM object is registered.

## Risks and edge cases
Because this is an interface, compatibility risk is mostly API shape. Renaming methods changes JMX attribute names. Returning raw directory strings can expose deployment paths through JMX. `getRatisRoles` uses a weakly typed `List<List<String>>`, so consumers depend on undocumented row/column ordering from the implementation.

## Test signals
Tests should verify the implementing MXBean registers and exposes these attributes, returns stable non-null strings for configured directories/host/port, preserves `ServiceRuntimeInfo` attributes, and keeps `getRatisRoles` structure compatible with existing JMX consumers.
