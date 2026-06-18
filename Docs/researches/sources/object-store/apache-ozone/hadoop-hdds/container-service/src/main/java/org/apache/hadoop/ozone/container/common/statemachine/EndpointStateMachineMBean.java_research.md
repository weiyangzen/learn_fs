# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/EndpointStateMachineMBean.java

## Purpose
This interface defines the JMX view of a single datanode endpoint connection to SCM or Recon.

## Important APIs and Types
It exposes `getMissedCount()`, `getAddressString()`, `getState()`, `getVersionNumber()`, `getLastSuccessfulHeartbeat()`, and `getType()`. The state type is `EndpointStateMachine.EndPointStates`.

## Control Flow
There is no implementation control flow in the interface. `EndpointStateMachine` implements it, and `SCMConnectionManagerMXBean.getSCMServers()` returns a list of these views for management tooling.

## State and Persistence Behavior
No state is stored here. The interface shape determines what endpoint state can be observed over JMX.

## Dependencies and Integration Points
It is coupled to `EndpointStateMachine.EndPointStates` and the Hadoop JMX/MBeans registration path in `SCMConnectionManager`.

## Risks
Any incompatible signature changes affect JMX clients. Returning enum values rather than strings can expose implementation names as management contract.

## Test Signals
Tests should check that `EndpointStateMachine` satisfies this contract and that `SCMConnectionManager` returns endpoint beans through its MXBean.
