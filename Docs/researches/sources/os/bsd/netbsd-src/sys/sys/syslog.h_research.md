# File Research: sources/os/bsd/netbsd-src/sys/sys/syslog.h

This header defines syslog priority/facility encoding, userland syslog APIs, reentrant syslog state, and kernel logging prototypes.

Key interface details:
- Defines `_PATH_LOG` as `/var/run/log`.
- Defines priorities `LOG_EMERG` through `LOG_DEBUG`, plus `LOG_PRIMASK` and `LOG_PRI`.
- Under `SYSLOG_NAMES`, defines `CODE` and name tables for priorities and facilities, including deprecated aliases.
- Defines facilities such as `LOG_KERN`, `LOG_USER`, `LOG_MAIL`, `LOG_DAEMON`, `LOG_AUTH`, `LOG_LOCAL0` through `LOG_LOCAL7`.
- Defines `LOG_NFACILITIES`, `LOG_FACMASK`, and `LOG_FAC`.
- Defines `LOG_MASK` and `LOG_UPTO`.
- Defines `openlog` options: `LOG_PID`, `LOG_CONS`, `LOG_ODELAY`, `LOG_NDELAY`, `LOG_NOWAIT`, `LOG_PERROR`, `LOG_PTRIM`, `LOG_NLOG`.
- For userland, defines `struct syslog_data`, `SYSLOG_DATA_INIT`, standard APIs, reentrant `_r` APIs, and `syslogp`/`vsyslogp`.
- For kernel, declares `logpri`, `log`, `vlog`, `addlog`, and `logwakeup`.

Research notes:
- Priority and facility are packed into a single integer; low bits store priority and higher bits store facility.
- The userland reentrant APIs are version-renamed with `__RENAME(...60)` to preserve libc ABI compatibility.
- Kernel and userland use the same priority/facility constants but expose different function surfaces.
