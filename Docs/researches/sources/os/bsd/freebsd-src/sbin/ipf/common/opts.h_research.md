# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/opts.h

## Purpose
Defines shared IPFilter command option bit flags and small portability helpers.

## Main Elements
- Detects Solaris builds.
- Defines `OPT_*` flags for remove, debug, raw, log, show/list, verbose, dry-run, counters, line numbers, queues, inactive list, NAT/state views, flush/clear, hex/ascii, no-resolve, purge, and related modes.
- Aliases `OPT_STAT` and `OPT_LIST`.
- Defines `STRERROR()` compatibility.
- Declares global `opts`.

## Dependencies And Integration
Included by `ipf.h`, then shared by many IPFilter utilities and parser actions.

## Risk Notes
`opts` is a process-global behavior switch; conflicting option bits can materially change ioctl targets and side effects.
