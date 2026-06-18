# sources/distributed-fs/xrootd/src/XrdCl/XrdClPostMaster.hh

## Purpose

This header declares `PostMaster`, the public facade for XrdCl's asynchronous network messaging subsystem. It hides `PostMasterImpl` and exposes lifecycle, send, redirect, channel query, event-handler, and connection-control APIs.

## Important APIs, Types, And Functions

Important methods include `Initialize`, `Finalize`, `Start`, `Stop`, `Reinitialize`, `Send`, `Redirect`, `QueryTransport`, `RegisterEventHandler`, `RemoveEventHandler`, `GetTaskManager`, `GetJobManager`, `ForceDisconnect`, `ForceReconnect`, `NbConnectedStrm`, `SetOnDataConnectHandler`, `SetOnConnectHandler`, `SetConnectionErrorHandler`, `NotifyConnectHandler`, `NotifyConnErrHandler`, `CollapseRedirect`, `DecFileInstCnt`, and `IsRunning`.

## Control Flow

The header contract makes `PostMaster` the layer that callers use instead of constructing channels directly. Messages are submitted with a destination `URL`, `Message*`, `MsgHandler*`, statefulness flag, and expiration time. Channel-level event and disconnect operations are all URL-addressed.

## State And Persistence Behavior

The visible class owns a `std::unique_ptr<PostMasterImpl>`. All state is hidden in the implementation. No persistence is part of the public contract.

## Dependencies And Integration Points

The header depends on `Status`, `URL`, `PostMasterInterfaces`, `XrdSysPthread`, and forward declarations for `Poller`, `TaskManager`, `Channel`, `JobManager`, and `Job`. It is used by `DefaultEnv`, operations, file/filesystem code, and transport/channel internals.

## Risks And Edge Cases

The `Send` comment warns about deadlocks if callers hold locks that callbacks also need. Many APIs accept raw handler/job pointers with async behavior; lifetime must outlive registration or be transferred according to channel/job manager conventions. `Reinitialize` is promised for fork handling but implemented as a no-op.

## Test Signals

Public API tests should verify lifecycle idempotence, URL-addressed handler registration/removal, disconnected URL errors, async send insertion status, and no deadlocks when callbacks are delivered through `JobManager`.
