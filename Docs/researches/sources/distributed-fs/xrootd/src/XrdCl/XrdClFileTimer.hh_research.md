# sources/distributed-fs/xrootd/src/XrdCl/XrdClFileTimer.hh

## Purpose
`XrdClFileTimer.hh` declares `FileTimer`, a `Task` implementation used to generate periodic timeout events for file state handlers in recovery mode.

## Important APIs, Types, And Functions
`FileTimer` inherits from `Task`, names itself `"FileTimer task"`, and exposes `RegisterFileObject`, `UnRegisterFileObject`, `Lock`, `UnLock`, and virtual `Run`. Its private state is `std::set<FileStateHandler*> pFileObjects` protected by `XrdSysMutex`.

## Control Flow
Clients register `FileStateHandler` pointers. `Run` later iterates those pointers and calls `Tick`; explicit `Lock` and `UnLock` allow `ForkHandler` to freeze timer activity during process fork.

## State And Persistence Behavior
State is an in-memory raw-pointer set. The timer does not own file state handlers, so users must unregister before destruction. There is no durable persistence.

## Dependencies And Integration Points
The class depends on `XrdSysPthread` and `XrdClTaskManager`. It integrates with `DefaultEnv` task scheduling and `ForkHandler`.

## Risks And Test Signals
Raw pointer registration can leave dangling pointers if handlers are destroyed without unregistering. Tests should include duplicate registration, unregistering absent objects, tick scheduling, and fork lock/unlock interactions.
