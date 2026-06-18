# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiProvider.hh

Purpose: defines the abstract provider contract for SSI. Providers answer resource availability, create service objects, initialize server-side operation, and accept client-side tuning options.

Important APIs/types: `Control()` handles future control operations with default `CTL_None` support. `GetService()` returns an `XrdSsiService` for client or server use, defaulting to `ENOTSUP`. `SsiVersion`/`GetVersion()` support ABI compatibility. Pure virtual `Init()` and `QueryResource()` are mandatory. Optional hooks include `ResourceAdded()`, `ResourceRemoved()`, deprecated `SetCBThreads()`, `SetConfig()`, `SetSpread()`, and `SetTimeout()`. Enums include `rStat` and timeout type `tmoType`.

Control flow and state: this header declares behavior only; implementations must be thread-safe except for initialization. The protected destructor documents that provider objects are plugin/global owned and not explicitly deleted by SSI.

Dependencies and integration: depends on `XrdSsiErrInfo` and `XrdSsiResource`, with forward declarations for cluster/logger/service. It is central to plugin integration on both client and server. Risks include ABI/version mismatches, provider methods not being thread-safe, callers relying on optional configuration methods that providers ignore, and ambiguous error semantics for `EAGAIN`/`EBUSY` later interpreted by session open. Test signals should include mock providers for all `rStat` values, initialization failure logging, version checks, and client option validation.
