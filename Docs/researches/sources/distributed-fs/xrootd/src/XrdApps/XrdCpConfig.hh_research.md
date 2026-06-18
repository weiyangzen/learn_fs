<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpConfig.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdCpConfig.hh

Purpose: declares the `XrdCpConfig` data model, option bit constants, parser entry point, and private helpers used by `xrdcp` configuration processing.

Important APIs/types/functions: nested `defVar` stores legacy `-DI`/`-DS` definitions; public fields expose parsed destination/source opaque strings, program name, rate limits, parallelism, proxy host/port, option mask, debug/verbose flags, source/stream counts, retry policy, checksum state, file lists, ZIP path, and additional checksums. `Want()` tests option bits. Constants define `Do*` flags and option ids for checksum, force, recursion, TPC, TLS, xattr, ZIP, continue, retry policy, and more. `Config()` is the public parser.

Control flow: consumers construct `XrdCpConfig`, call `Config(argc, argv, Opts)`, then inspect public fields and linked file lists to drive copy execution. Private methods implement validation and parsing details.

State/persistence: all state is process-local and owned by the object; destructor frees linked lists and helper objects. No persistence is declared here.

Dependencies/integration: forward-declares `XrdCks`, `XrdCksCalc`, `XrdCpFile`, and `XrdSysError`; includes `XrdCksData`; exposes option flags consumed by the copy application.

Risks/test signals: the class exposes many mutable public fields, so invariants depend on callers not mutating parsed state inconsistently after `Config()`. `OpSpec` is a 64-bit mask with both character option ids and bit flags nearby, making new-option allocation error-prone. Tests should assert default constructor values, destructor ownership, `Want()` behavior, unique bit assignments, and compatibility of public fields with downstream copy code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpConfig.hh -->
