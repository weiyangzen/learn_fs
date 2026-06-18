# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipmon/ipmon.c

`ipmon.c` implements the IPFilter log monitor. It reads filter, NAT, and state log streams and writes formatted logs to stdout, files, binary logs, syslog, or configured action savers.

Major behaviors:
- Supports log source selection for filter (`IPL_NAME`), NAT (`IPNAT_NAME`), and state (`IPSTATE_NAME`) logs.
- Supports daemon mode, syslog mode, binary log output, tail mode for regular files, pidfile writing, log flushing, name resolution, numeric ports, body/header hex dumps, and config-driven actions.
- Initializes protocol and TCP/UDP service lookup tables from system databases.
- Reads from up to three log sources with `select()`, handling character devices and regular files differently.
- Handles SIGHUP by reopening output logs, reloading service/protocol tables, and reloading the config file.

Formatting:
- `print_ipflog()` formats filter log entries with timestamps, interface/group/rule, pass/block/log flags, IPv4/IPv6 addresses, ports, protocol, lengths, TCP flags/seq/ack/window in verbose mode, ICMP/ICMPv6 names, fragment info, state/frag/NAT/log/nattag markers, low TTL/out-of-window/bad/NAT/broadcast/multicast flags, and block reason text.
- `print_natlog()` formats NAT lifecycle events (`NEW`, `FLUSH`, `CLONE`, `EXPIRE`, `DESTROY`, `PURGE`) and NAT rule types (`MAP`, `RDR`, `BIMAP`, mapblock, rewrite, encap, divert), including packet/byte counts on expiry/flush.
- `print_statelog()` formats state lifecycle events (`NEW`, `CLONED`, `EXPIRE`, `CLOSE`, `FLUSH`, `INTERMEDIATE`, `REMOVE`, `KILLED`, `UNLOAD`) and forward/backward counters.
- `dumphex()` writes hex plus printable ASCII, to syslog or file.

Configuration interaction:
- When a config file is loaded, filter log lines are passed to `check_action()` from `ipmon_y.y`; matching configured actions can suppress the default output and instead execute saver callbacks.

Notable implementation details:
- Uses static sequence counters per log type to report missed entries.
- Uses a fixed global `line[2048]` formatting buffer with extensive `sprintf`/`strcpy` appends.
- The default-log selection condition repeats `config.logsrc[0].logtype` three times, which looks like a copy/paste bug meant to check all three sources.
