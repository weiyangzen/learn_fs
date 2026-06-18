# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/log.c

Logging support for `dhcp6leased`.

It initializes stderr logging in debug mode or syslog logging otherwise, tracks a process name and verbosity level, preserves `errno` across logging calls, and provides warn/warnx/info/debug/fatal/fatalx helpers. Debug logging is gated by verbosity; fatal helpers log with process context and exit.
