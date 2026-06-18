# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/SCMConnectionManagerMXBean.java

## Purpose
This interface defines the JMX management view for the datanode SCM connection manager.

## Important APIs and Types
The single method `getSCMServers()` returns `List<EndpointStateMachineMBean>`, allowing management clients to inspect endpoint addresses, states, missed counts, versions, heartbeat timestamps, and type.

## Control Flow
No control flow is implemented here. `SCMConnectionManager` implements it and registers itself as an MBean in its constructor.

## State and Persistence Behavior
No state is stored in the interface. It shapes the observable endpoint collection contract.

## Dependencies and Integration Points
It depends on `EndpointStateMachineMBean` and the MBeans registration in `SCMConnectionManager`.

## Risks
Changing the method name or return type can break JMX consumers and dashboards. The method name says SCM servers, but implementations include Recon endpoints too.

## Test Signals
Tests should assert that the registered connection-manager MBean exposes all active SCM and Recon endpoint MBeans through this method.
