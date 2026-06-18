# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiLogging.cc

Purpose: implements the XRootD log plugin initializer that loads an SSI logging callback provider from configuration. It lets `-l@` route XRootD logging into a provider-defined SSI callback.

Important APIs and control flow: local `ConfigLog(const char *cFN)` opens the config, scans for `ssi.loglib` or `ssi.svclib`, prefers `loglib` and falls back to `svclib`, loads the selected shared library with `XrdSysPlugin`, and looks up `XrdSsiLoggerMCB` if global `msgCB` was not already set by dynamic initialization. `XrdSysLogPInit()` is the exported C entry point; it calls `ConfigLog()` and returns `msgCB`. `XrdVERSIONINFO` registers plugin version information.

State and persistence: global state is `XrdSsi::msgCB`; loaded plugins are persisted with `myLib->Persist()` when a callback is available. No file writes occur. Dependencies include `XrdOucStream` config parsing, `XrdSysPlugin`, version macros, and errno text conversion.

Integration points: used by XRootD's logging plugin mechanism, not by normal SSI request flow. Risks include config parse errors, ambiguous fallback from `loglib` to `svclib`, error message typo saying callback "was found" when it likely means not found, plugin symbol type assumptions, and persistence only after callback discovery. Test signals should include configs with only `ssi.svclib`, only `ssi.loglib`, missing directives, invalid paths, symbol missing, and a plugin that sets `msgCB` during load.
