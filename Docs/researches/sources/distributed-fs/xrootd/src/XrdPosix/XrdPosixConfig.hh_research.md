## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixConfig.hh

Purpose: declares the static configuration facade for XrdPosix runtime setup and status.

Important APIs/types: `XrdPosixConfig` static methods `conTracker`, `EnvInfo`, `initStat`, `SetConfig`, `OpenFC`, `SetEnv` overloads, `setOids`, and `Stats`; private helpers for cache/env/debug/IP/device initialization.

Control flow: callers do not instantiate meaningful state; all behavior is static and affects process globals. `OpenFC()` bridges configuration-aware open decisions into an `XrdPosixInfo` result.

State and persistence: no instance fields. The implementation mutates `XrdPosixGlobals` and `XrdCl::DefaultEnv`.

Dependencies/integration: forward-declares `XrdOucEnv`, `XrdOucPsx`, `XrdScheduler`, `XrdPosixInfo`, `XrdSecsssCon`, and `XrdSysLogger`; includes POSIX types. It is a central integration point for plugins/server-side setup.

Risks: static-only design makes tests sensitive to global residue between cases. Missing explicit reset API. `SetEnv` names include internal keys not obvious from the header.

Test signals: isolate configuration tests with process reset or explicit cleanup; verify `OpenFC()` behavior with cache direct-open info; check that `initStat()` stable defaults match target platform.
