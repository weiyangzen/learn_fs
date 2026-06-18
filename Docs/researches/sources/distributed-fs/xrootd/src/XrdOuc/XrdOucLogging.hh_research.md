<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLogging.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLogging.hh

Purpose: Declares the logging configuration facade used by servers and clients to centralize XRootD log setup.

APIs and control flow: `configLogInfo` carries the raw log argument, environment, instance name, config filename, version retention count, and high-resolution timestamp flag. `configLog()` is the public static entry point. Private helpers parse logging plugin argv and comma-delimited option values.

State and persistence: The header itself holds no instance state. Configuration effects are process-level: logger setup, plugin image lifetime, exported environment variables, and possible stderr forwarding created by the implementation.

Dependencies and integration: Forward-declares `XrdSysError` and `XrdOucEnv` so call sites can pass the active error router and environment without pulling in implementation headers.

Risks and test signals: The contract relies on `logArg` being non-null and stable during the call. Tests should validate `configLogInfo` defaults, public API compatibility for plugin users, and behavior when optional fields such as `xrdEnv`, `iName`, or `cfgFn` are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLogging.hh -->
