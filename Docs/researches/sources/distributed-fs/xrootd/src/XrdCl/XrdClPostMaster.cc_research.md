# sources/distributed-fs/xrootd/src/XrdCl/XrdClPostMaster.cc

## Purpose

This file implements `PostMaster`, the central XrdCl hub for asynchronous message delivery, channel creation, polling, task execution, job callbacks, transport queries, redirects, and forced connection lifecycle operations.

## Important APIs, Types, And Functions

`PostMasterImpl` owns `Poller`, `TaskManager`, `JobManager`, a channel map keyed by `URL::GetChannelId()`, a non-owning finalize set, mutexes, and global connect/error handlers. `PostMaster::Initialize`, `Start`, `Stop`, and `Finalize` manage subsystem lifecycle. `Send` obtains/creates a `Channel` and delegates. `Redirect` delegates to `RedirectorRegistry`. Query/event/disconnect/reconnect methods locate channels and delegate. `CollapseRedirect` replaces an alias channel with an active channel labeled by a redirected URL. `PostMasterImpl::GetChannel` creates channels with the protocol `TransportHandler`.

## Control Flow

Initialization reads `PollerPreference`, creates and initializes a poller, then initializes the job manager. Start order is poller, task manager, job manager; failures roll back already-started subsystems. Stop order is job manager, poller, task manager. Finalize stops job callbacks, copies the finalize set, finalizes channels, clears the channel map, and finalizes the poller.

For send paths, `GetChannel` locks the map, locates or creates a `Channel` using `TransportManager::GetHandler(protocol)`, stores a `shared_ptr` with a custom deleter that removes it from the finalize set, then returns it. Most public channel operations use this helper or locked map lookup.

## State And Persistence Behavior

State is process-local. Channels are shared pointers in `pChannelMap`; the finalize set tracks live raw channel pointers for cleanup. `pRunning` and `pInitialized` gate lifecycle methods. Global connection callbacks are stored under `pMtx` and queued on `JobManager`. There is no disk persistence.

## Dependencies And Integration Points

PostMaster depends on `PollerFactory`, `XRootDTransport`, `Message`, `DefaultEnv`, `TaskManager`, `JobManager`, `TransportManager`, `Channel`, `RedirectorRegistry`, and `Log`. It is accessed through `DefaultEnv` by operations and transport code.

## Risks And Edge Cases

`Finalize` assumes no concurrency because poller and job manager are stopped; callers must respect lifecycle ordering. `NotifyConnectHandler` queues the same stored `Job` pointer with newly allocated `URL` args, so the job implementation must tolerate repeated runs and own/free args as expected by `JobManager`. `CollapseRedirect` retries recursively if the map changes; pathological churn could recurse repeatedly. `ForceDisconnect` erases channels before delegation, so callers cannot query that channel afterward. `Reinitialize` is a stub returning true and does not rebuild post-fork resources.

## Test Signals

Tests should cover lifecycle ordering/failure rollback, send channel creation, protocol handler absence, channel map reuse by channel ID, forced disconnect/reconnect, redirect collapse aliasing, global connect/error handler queuing, and finalization while channels remove themselves from the finalize set.
