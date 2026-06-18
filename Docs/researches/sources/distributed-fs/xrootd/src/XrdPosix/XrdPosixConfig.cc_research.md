## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixConfig.cc

Purpose: implements global configuration and initialization hooks for the POSIX layer, including scheduler/logger wiring, client environment settings, cache setup, connection cleanup tracking, default stat fields, and statistics formatting.

Important APIs/functions: `conTracker`, `EnvInfo`, `initCCM`, `initEnv(char*)`, `initEnv(XrdOucEnv&,...)`, `initStat`, `initXdev`, `OpenFC`, `SetConfig`, `SetDebug`, `SetEnv` overloads, `SetIPV4`, `setOids`, and `Stats`.

Control flow: `SetConfig()` is the main entry point from `XrdOucPsx`: it installs loggers, configures name-to-name PFN/LFN translation, applies client environment values, debug/trace, response-handler cache size, delayed-destroy retry policy, optional automatic pgread/TLS behavior, and either external cache, cache context manager, or memory cache. `initEnv()` parses `XRDPOSIX_CACHE` CGI-style options into `XrdRmc::Parms` and preread parameters. `conTracker()` registers a postmaster connect handler and returns a cleanup handler that can disconnect tracked SSS contacts.

State and persistence: writes many `XrdPosixGlobals` values: scheduler, cache, logger, name mapper, stats/tracing flags, directory-list flags, delayed-destroy settings, and feature booleans. It updates `XrdCl::DefaultEnv`. No files are persisted here, but cache plugins may persist data.

Dependencies/integration: integrates `XrdCl::DefaultEnv`, `JobManager`, `PostMaster`, `XrdOucPsx`, `XrdOucCache`, `XrdRmc`, `XrdSecsssCon`, `XrdSysError`, tracing, stats, and file response-handler configuration.

Risks: global mutable configuration is order-sensitive. `initXdev()` uses `stat("/tmp")` after POSIX macro interposition may be active. `Stats()` manually sizes XML-like text and returns `0` on truncation after partial formatting. `optsf` suffix uses `strdup()` and is not freed. Cache global can be overwritten by config paths.

Test signals: configure external cache, memory cache, and no cache; parse numeric suffixes and invalid values; directory-list flag precedence; IPv4 vs all-stack setting; stats buffer length query and truncation; delayed destroy parameters; auto pgread enablement.
