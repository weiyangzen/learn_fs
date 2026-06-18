# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/SCMConnectionManager.java

## Purpose
`SCMConnectionManager` owns the set of SCM and Recon RPC endpoint state machines used by the datanode. It creates protocol proxies, wraps them in endpoint state holders, exposes them over JMX, and closes them during shutdown or reconfiguration.

## Important APIs and Types
Public APIs include `addSCMServer()`, `addReconServer()`, `removeSCMServer()`, `getValues()`, `getSCMServers()`, `getNumOfConnections()`, `close()`, and explicit read/write lock methods. It implements `Closeable` and `SCMConnectionManagerMXBean`.

## Control Flow
The constructor registers an `HddsDatanode:SCMConnectionManager` MBean and reads the RPC timeout. Add methods take the write lock, reject duplicates, set the correct protobuf RPC engine, create an RPC proxy with retry policy, wrap the proxy in `StorageContainerDatanodeProtocolClientSideTranslatorPB`, create an `EndpointStateMachine`, mark it passive for Recon or active for SCM, and store it. Removal closes but does not force endpoint state to `SHUTDOWN`, avoiding false fatal shutdown signals from in-flight tasks.

## State and Persistence Behavior
The endpoint map is in-memory and guarded by a read/write lock. There is no durable persistence. Closing cleans endpoint RPC resources and unregisters the MBean.

## Dependencies and Integration Points
It depends on Hadoop RPC, retry policies, UGI, NetUtils, HDDS server utility config, and `EndpointStateMachine`. `InitDatanodeState` adds endpoints; running endpoint tasks iterate `getValues()`; `StateContext` separately tracks endpoint queues.

## Risks
Endpoint creation performs network/RPC setup under the write lock. If `StateContext.addEndpoint()` fails after adding an SCM server, the connection manager and context can diverge. `getValues()` returns a snapshot, so callers must tolerate concurrent removals. JMX registration failure behavior depends on `MBeans.register`.

## Test Signals
Tests should cover duplicate add, SCM vs Recon passive flag, removal without setting shutdown, close/unregister behavior, lock-protected snapshots, retry policy construction, and JMX server list shape.
