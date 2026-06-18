## sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogPI.hh

Purpose: defines the logging plugin ABI used by `XrdSysLogging`.

Important APIs/types/functions: `XrdSysLogPI_t` is the per-message callback type taking generation time, thread id, message text, and message length. `XrdSysLogPInit_t` is the plugin initialization entry point type returning an `XrdSysLogPI_t` and accepting a config file name plus plugin-specific argv/argc. Documentation also prescribes `extern "C" XrdSysLogPInit(...)` and optional version declaration via `XrdVERSIONINFO`.

Control flow: the logging system loads a plugin initializer, calls it once, stores the returned callback, then invokes the callback per log message either synchronously or from the async forwarding thread.

State and persistence: no state in the header. Plugin implementations own any state created during init and must keep callback state alive.

Dependencies and integration: includes `<sys/time.h>`. Integrated with `XrdSysPlugin` version checking and `XrdSysLogging::Configure`.

Risks: ABI stability is critical. Callback thread-safety requirements differ by sync versus async mode. Message text is length-delimited but also expected to be null-terminated by current forwarding code.

Test signals: plugin loading, missing init symbol, versioned plugin declarations, synchronous concurrent callbacks, async single-threaded callback ordering, and handling of `tID == 0` captured stderr messages.
