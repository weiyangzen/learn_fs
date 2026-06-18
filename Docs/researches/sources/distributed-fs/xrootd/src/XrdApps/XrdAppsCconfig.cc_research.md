<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdAppsCconfig.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdAppsCconfig.cc

Purpose: implements `cconfig`, a utility that reads an XRootD configuration file through `XrdOucStream`, evaluates conditional/directive substitution for a selected host/instance/program, optionally filters requested directives, captures the resulting expanded config, and writes it to stdout or a file.

Important APIs/types/functions: `inList()` checks directive names against static exception lists; `cfOut()` writes captured config to `-o` with mode `0644`; `Usage()` prints CLI syntax; `main()` handles `-c`, `-h`, `-n`, `-o`, and `-x`, builds the `XRDINSTANCE`-style stream identity, attaches the config fd to `XrdOucStream`, and drives capture/echo.

Control flow: options are parsed, the host is resolved through `XrdNetAddr`, selector directives are stored in an `XrdOucNList_Anchor`, and the config is opened. Each first word is checked against the optional selector queue. Certain directives in `noSub` are read with environment substitution disabled so message/copy command strings are preserved. Directives in `ifChk` are scanned for `if` and evaluated with `XrdOucUtils::doIf()`, suppressing echo if the condition fails. Everything else consumes the rest of the line and echoes the captured version.

State/persistence: the main state is captured expanded config in an `XrdOucString`. Persistence happens only when `-o` is provided, via truncating write to the chosen output file.

Dependencies/integration: depends on XRootD utility parsing and conditional-expression machinery: `XrdOucStream`, `XrdOucEnv`, `XrdOucNList`, `XrdOucUtils::InstName()`, `XrdOucUtils::doIf()`, `XrdNetAddr`, and `XrdSysError`.

Risks/test signals: directive exception lists are hard-coded and can drift from server config behavior. `cfOut()` returns on write failure without closing the fd on that path. Tests should cover host/name/program selection, directive filtering, `if` evaluation, no-substitution directives, slash scanning for `frm.xfr.copycmd`, output-file errors, and config read errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdAppsCconfig.cc -->
