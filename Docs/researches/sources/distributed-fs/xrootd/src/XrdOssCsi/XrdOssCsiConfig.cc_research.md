# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiConfig.cc

Purpose: implements runtime configuration parsing for the checksum-sidecar plugin. It handles plugin parameters, reads `csi.*` directives from the XRootD config file, and reports effective settings.

Important APIs/functions: `Init()` parses space-separated plugin parameters: `nofill`, `space=<name>`, `nomissing`, `prefix=<path-or-empty>`, `nopgextend`, and `noloosewrites`. It initializes trace defaults, honors `XRDDEBUG`, calls `readConfig()`, and logs outcomes. `readConfig()` opens the config file with `XrdOucStream`, captures plugin config blocks, and dispatches `csi.` directives. `ConfigXeq()` currently supports `trace`. `xtrace()` parses `all`, `debug`, `warn`, `info`, and `off`, including negative options to clear bits.

State/persistence: mutates `XrdOssCsiConfig` booleans, tag prefix, tag-file space name, and global `OssCsiTrace.What`. No persistent files are written.

Dependencies/integration: uses `XrdOucStream`, `XrdSysError`, `XrdOssCsiTrace`, and POSIX `open`. Risks include simplistic whitespace parameter parsing, unknown parameters silently ignored, config file absence treated as defaults but open errors fatal, and trace directive limited to config-file `csi.trace`. Tests should cover every parameter combination, invalid prefix, trace add/remove semantics, config-file read errors, and default logging.
