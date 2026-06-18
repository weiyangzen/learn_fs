
# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/ExternalCall.java

## Purpose

`ExternalCall<T>` adapts a `PrivilegedExceptionAction<T>` into a `Server.Call` that can be executed by the IPC handler machinery while an external caller waits for completion. It is used for postponed or externally triggered work that still needs IPC call accounting and response completion semantics.

## Important APIs, types, and functions

The constructor stores the action. `getRemoteUser()` is abstract for subclasses. `get()` blocks until completion and either returns the result or throws `ExecutionException`. `run()` executes the action and sends or aborts the response. `doResponse()` is the completion callback that records the error, marks `done`, and notifies waiters. `getDetailedMetricsName()` returns `(external)`.

## Control flow

The external caller creates a subclass, submits it as a `Server.Call`, and waits in `get()`. The IPC handler invokes `run()`, which calls `action.run()`, then `sendResponse()` on success or `abortResponse()` on failure. Response completion ultimately invokes `doResponse()`, which releases the waiter.

## State and persistence behavior

State is per-call and in-memory: action, atomic completion flag, result, and error. There is no durable state.

## Dependencies and integration points

It extends `Server.Call`, uses `RpcStatusProto`, and depends on `UserGroupInformation` for remote user attribution. Ozone tests such as `TestS3SecretRequestHelper` use stub subclasses.

## Risks and test signals

Wait/notify correctness is critical. `waitForCompletion()` loops on an `AtomicBoolean` while synchronizing on the same object; tests should cover normal completion, exception completion, interrupted waits, double response attempts, and postponed-call behavior.
