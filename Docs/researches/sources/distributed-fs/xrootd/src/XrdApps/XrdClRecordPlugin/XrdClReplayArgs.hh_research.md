<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClReplayArgs.hh -->
# sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClReplayArgs.hh

Purpose: defines `XrdCl::ReplayArgs`, the option parser and accessors for `xrdreplay`.

Important APIs/types/functions: constructor parses `--help`, `--print`, `--create`, `--truncate`, `--long`, `--json`, `--summary`, `--replace`, `--suppress`, `--verify`, and `--speed`; `usage()` prints help and exits; accessors expose booleans, speed, regex replacements, and optional input path.

Control flow: `getopt_long()` populates option flags. Create/truncate imply print/simulated mode. JSON enables long and summary output. Verify forces print mode and disables create/truncate/json. At most one positional path is accepted; otherwise stdin is used.

State/persistence: stores parsed options in memory only. No durable state.

Dependencies/integration: used by `XrdClReplay.cc`; depends on `getopt_long`, `std::vector`, `std::string`, and `strtod`.

Risks/test signals: the short usage text contains typos, and the short option string includes `r:` and `x:` while long options accept required args. The condition `if (option_json && (option_long || option_summary)) option_long = option_summary = true;` only promotes JSON when one of long/summary was already set, despite main's JSON output expecting structured sections. Tests should cover option interactions, invalid speed values, repeated `--replace`, stdin input, too many positional arguments, verify overriding create/json, and JSON with no explicit long/summary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdApps/XrdClRecordPlugin/XrdClReplayArgs.hh -->
