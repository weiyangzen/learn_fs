## sources/user-network-fs/blobfuse2/component/xload/xcomponent.go

Purpose: Defines the internal xload stage interface and base implementation used by lister, splitter, and data manager.

Important APIs and flow: `XComponent` requires lifecycle (`Init`, `Start`, `Stop`), scheduling/processing, next-stage linkage, thread pool access, remote component access, name, and stats manager access. `XBase` stores those fields plus worker count. Its `Schedule` sends to the thread pool when present, otherwise calls `Process` synchronously. Default `Process` is a no-op returning zero.

State and dependencies: `XBase` holds mutable pipeline links and references to `ThreadPool`, `internal.Component`, and `StatsManager`. It logs synchronous process errors.

Risks: Default no-op behavior can hide miswired components; tests intentionally rely on it. `Schedule(nil)` is tolerated when no pool exists, but real pools expect non-nil work items. There is no synchronization around setting next/remote/stats fields, so setup must complete before workers start. Coverage appears through xload tests and direct default behavior tests.
