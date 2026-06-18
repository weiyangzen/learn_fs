# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/DNMXBean.java

## Purpose
JMX management interface for datanode runtime information.

## Important APIs, Types, And Functions
Extends `ServiceRuntimeInfo` and declares getters for hostname, datanode UUID, client RPC port, HTTP port, and HTTPS port.

## Control Flow
`HddsDatanodeService` fills a `DNMXBeanImpl` during startup and registers it with JMX so management clients can read the values.

## State And Persistence
No implementation state in the interface; state is held by the bean implementation and service runtime base.

## Dependencies And Integration Points
Integrated with Hadoop/HDDS metrics and JMX via `HddsUtils.registerWithJmxProperties`.

## Risks
String-returning ports are simple but require service startup to set them after bind. Missing HTTP/HTTPS policy branches may leave nulls.

## Test Signals
Signals include MXBean registration, visible hostname/UUID/ports in JMX, and runtime info inherited from `ServiceRuntimeInfo`.
