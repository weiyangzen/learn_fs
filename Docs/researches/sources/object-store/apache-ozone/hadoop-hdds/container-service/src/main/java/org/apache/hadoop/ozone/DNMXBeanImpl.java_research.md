# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/DNMXBeanImpl.java

## Purpose
Concrete JMX bean storing datanode identity, ports, and inherited service runtime/version information.

## Important APIs, Types, And Functions
Extends `ServiceRuntimeInfoImpl`, implements `DNMXBean`, and provides getters/setters for host name, datanode UUID, client RPC port, HTTP port, and HTTPS port.

## Control Flow
The datanode service constructs this bean with HDDS version info, sets start time and identity/ports as services bind, and registers it with JMX.

## State And Persistence
Mutable in-memory string fields hold identity and port values. Persistence is external only through JMX visibility.

## Dependencies And Integration Points
Depends on HDDS `VersionInfo` and service runtime base classes. Used directly by `HddsDatanodeService`.

## Risks
No synchronization protects setters/getters, though startup writes are mostly single-threaded. Nulls are possible for disabled or failed servers.

## Test Signals
Signals include service startup setting each field, JMX reads after HTTP/RPC bind, and unregistering the bean during shutdown.
