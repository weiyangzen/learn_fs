<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpConfig.cc -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdCpConfig.cc

Purpose: implements `XrdCpConfig`, the main command-line configuration parser and validator for `xrdcp`-style copy operations.

Important APIs/types/functions: static `opLetters` and `opVec` define short/long options; constructor initializes defaults; destructor releases file lists, checksum objects, proxy and parameter storage; `Config()` parses options, resolves destination/source files, validates conflicts, reads `--infiles`, and expands recursive local directories; numeric helpers `a2i`, `a2l`, `a2t`, `a2z`, and `a2x` validate values; `defCks()` configures checksum behavior; `defOpq()`, `defOpt()`, and `defPxy()` parse legacy opaque/define/proxy options; `Legacy()` supports old aliases; `ProcFile()` validates each source; `Usage()` prints detailed help.

Control flow: `Config()` allocates a parameter vector, processes legacy and modern options in one loop, applies mode side effects such as server implying silent/nopbar/force, enables make-path from `XRD_MAKEPATH`, then treats the final operand as destination. It resolves local destination metadata, processes sources from CLI and optional input file, enforces source counts and protocol restrictions, validates checksum/TPC/ZIP conflicts, and optionally expands local directories recursively into individual `XrdCpFile` entries.

State/persistence: builds an in-memory linked list of `XrdCpFile` sources and one destination object, stores option bits in `OpSpec`, checksum manager/calculator objects, proxy settings, rate limits, and totals for local files. It reads an input file list when requested but does not write files.

Dependencies/integration: depends on `XrdCpFile`, `XrdCksManager`, `XrdCksCalc`, `XrdCksData`, `XrdOucStream`, `XrdSysError`, `XrdSysE2T`, `getopt_long`, and XRootD version/license headers.

Risks/test signals: the ZIP/checksum conflict checks use bitwise `&` chains such as `OpSpec & DoZip & DoCksrc`, which do not test both flags as intended because the flag constants do not overlap. Error handling exits directly, making unit tests need process-level harnesses. `a2z()` reports invalid byte rates as "not a valid time." Tests should cover every option, legacy aliases, invalid numeric bounds, proxy parsing, checksum modes including `auto` and additional source checksums, TPC qualifiers, server/silent side effects, `--infiles`, recursive expansion, local/local rejection, stdin restrictions, remote recursive policy, ZIP conflicts, and environment-driven make-path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdCpConfig.cc -->
