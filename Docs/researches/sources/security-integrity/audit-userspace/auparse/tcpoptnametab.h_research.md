<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/tcpoptnametab.h -->
# sources/security-integrity/audit-userspace/auparse/tcpoptnametab.h

## Purpose
Maps TCP socket option ids to names.

## Important APIs, types, and functions
The `_S` table covers no-delay, max segment, cork, keepalive settings, sync/defer/window/info/congestion, MD5, repair, fast open, not-sent low-water, zero-copy receive, TCP-AO, and related options.

## Control flow
Generated `tcpoptname_i2s` is used by `interpret.c:print_tcp_opt_name` when socket option level is `IPPROTO_TCP`.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks Linux TCP headers and is selected by `print_a2` for socket option syscalls.

## Risks and test signals
Risks are new TCP option drift and platform availability differences. Tests should cover common options, newer TCP-AO ids, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/tcpoptnametab.h -->
