# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/statemachine/EndpointStateMachine.java

## Purpose
`EndpointStateMachine` holds state for one SCM or Recon RPC endpoint. It tracks endpoint state transitions, missed heartbeat count, version response, last successful heartbeat, passive/active type, and exposes this data through JMX.

## Important APIs and Types
The class implements `Closeable` and `EndpointStateMachineMBean`. Public methods include `lock()/unlock()`, `getVersion()/setVersion()`, `getState()/setState()`, `getExecutorService()`, `incMissed()`, `zeroMissedCount()`, `logIfNeeded(Exception)`, `setPassive()`, `getLastSuccessfulHeartbeat()`, and `getType()`. The `EndPointStates` enum moves through `GETVERSION`, `REGISTER`, `HEARTBEAT`, and `SHUTDOWN`.

## Control Flow
State-specific endpoint tasks use the endpoint lock and single-thread executor to serialize calls. Missed communications call `logIfNeeded()`, which throttles SCM warnings by `getLogWarnInterval(conf)` and Recon warnings by ten times that interval, then increments the missed count.

## State and Persistence Behavior
All state is in memory. Closing shuts down the RPC translator and endpoint executor. Last heartbeat is stored as a `ZonedDateTime` and exposed as epoch seconds for JMX.

## Dependencies and Integration Points
It wraps `StorageContainerDatanodeProtocolClientSideTranslatorPB`, detects Recon via `ReconDatanodeProtocolPB`, and is created by `SCMConnectionManager`. Endpoint tasks in the states/endpoint package advance the enum and update version/heartbeat state.

## Risks
`setState()` has no transition validation, so callers must preserve legal progression. `getType()` assumes the endpoint translator is available and exposes the underlying proxy. Executor shutdown is not awaited. Logging duration is computed from missed count times SCM heartbeat interval, also for Recon.

## Test Signals
Tests should validate enum progression, missed-count throttling, passive endpoint type, JMX getters, close behavior, and state/version updates during simulated version/register/heartbeat task flows.
