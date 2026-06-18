## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTransfer.hh

Purpose: declares the transfer worker class and its helper methods. The class is instantiated per worker thread and owns command objects used to run configured copy operations.

Important APIs/types: public static `checkFF()` inspects and ages fail files; `Init()` starts global queue/worker infrastructure; `Start()` is the worker loop. Private methods separate inbound fetch, outbound throw, fail-file creation/checking, command setup, directory creation tracking, migration validation, and migration completion. Static `pMutex`/`pTab` coordinate remote directory tracking across workers. Per-worker fields include four `XrdOucProg *` command slots, the current `XrdFrmXfrJob *`, and `cmdBuff`.

State and persistence: this header shows mixed static and per-worker state. Durable state is handled by implementation through fail files, xattrs, sidecars, and namespace notifications.

Dependencies and integration: forward declares transfer helper structs, jobs, and `XrdOucProg`; includes hash and thread primitives. Called from `XrdFrmXfrDaemon::Init()` and transfer worker threads.

Risks and test signals: the current job pointer is a mutable member, so one `XrdFrmTransfer` object must not be shared across threads. Tests should verify one object per thread and command object setup for all four transfer directions.
