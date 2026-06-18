## sources/distributed-fs/xrootd/src/XrdSys/XrdSysIOEvents.hh

Purpose: declares the public event polling architecture under `XrdSys::IOEvents`.

Important APIs/types/functions: `CallBack` exposes event flags `ReadyToRead`, `ReadTimeOut`, `ReadyToWrite`, `WriteTimeOut`, `ValidEvents`, pure virtual `Event()`, and optional `Fatal()`/`Stop()` hooks. `Channel` exposes `Delete`, `Enable`, `Disable`, `GetCallBack`, `GetEvents`, `GetFD`, `SetCallBack`, `SetFD`, and constructor. `Poller` exposes `Create`, `Stop`, constructor/destructor, and protected virtual backend methods `Begin`, `Exclude`, `Include`, `Modify`, `Shutdown`.

Control flow: users create a specialized `Poller` through `Poller::Create()`, construct `Channel` objects against it, enable events, and react through `CallBack`. Backend implementations subclass `Poller` and use protected helpers to synchronize command dispatch and callback execution.

State and persistence: channel and poller fields define all runtime state: lists, locks, fd, callback, timeouts, status, command pipe, and wake flag. The API explicitly requires callers to detach/disable channels before closing descriptors.

Dependencies and integration: depends on `poll.h`, pthread wrappers, and atomic macros. Platform backends are included by the `.cc` file.

Risks: destructor for `Channel` is private, so callers must use `Delete()`. Callback code may deadlock if it manages unrelated channels without a clear lock model. Event bits and callback event bits are related but distinct masks.

Test signals: API-level lifecycle tests, callback return false behavior, fatal and stop hook behavior, timeout settings per read/write, and compile tests for custom backend subclasses.
