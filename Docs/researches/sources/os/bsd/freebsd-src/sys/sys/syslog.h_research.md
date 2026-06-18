# File Research: sources/os/bsd/freebsd-src/sys/sys/syslog.h

## Scope

This header defines the FreeBSD syslog priority/facility namespace, log socket paths, openlog/setlogmask option flags, optional name lookup tables, and userland syslog function prototypes.

## APIs And Constants

- Defines log socket paths `_PATH_LOG` and `_PATH_LOG_PRIV`.
- Defines priorities `LOG_EMERG` through `LOG_DEBUG`, `LOG_PRIMASK`, `LOG_PRI()`, and `LOG_MAKEPRI()`.
- Defines facilities `LOG_KERN`, `LOG_USER`, `LOG_MAIL`, `LOG_DAEMON`, `LOG_AUTH`, `LOG_SYSLOG`, `LOG_LPR`, `LOG_NEWS`, `LOG_UUCP`, `LOG_CRON`, `LOG_AUTHPRIV`, `LOG_FTP`, `LOG_NTP`, `LOG_SECURITY`, `LOG_CONSOLE`, and `LOG_LOCAL0` through `LOG_LOCAL7`.
- Defines `LOG_NFACILITIES`, `LOG_FACMASK`, and `LOG_FAC()`.
- When `SYSLOG_NAMES` is enabled, defines `CODE`, `prioritynames[]`, and `facilitynames[]`, including deprecated aliases and internal `none`/`mark` entries.
- Defines `LOG_MASK()` and `LOG_UPTO()` for `setlogmask()`.
- Defines `openlog()` option flags `LOG_PID`, `LOG_CONS`, `LOG_ODELAY`, `LOG_NDELAY`, `LOG_NOWAIT`, and `LOG_PERROR`.
- In userland, declares `closelog()`, `openlog()`, `setlogmask()`, `syslog()`, and BSD-visible `vsyslog()`.
- In kernel builds, defines pseudo-priority `LOG_PRINTF`.

## Control Flow And Integration

- Priority occupies the low three bits and facility occupies higher bits, so call sites build a single integer selector.
- Userland prototypes avoid directly including a varargs header by using `__va_list` from `<sys/_types.h>`.
- The optional name arrays are static header data used by parsers such as syslog configuration tools when `SYSLOG_NAMES` is requested.

## Dependencies

- Userland declarations depend on `<sys/cdefs.h>` for declaration and printf-format attributes and `<sys/_types.h>` for `__va_list`.
- Facility and priority constants must stay aligned with `syslogd(8)` string mappings and existing syslog protocol expectations.

## Risks And Invariants

- Priority encoding assumes three priority bits; changing `LOG_PRIMASK` or facility shifts would break existing logs and parsers.
- Facility values are externally visible and must remain stable for configuration compatibility.
- `LOG_NDELAY` and `LOG_ODELAY` comments document historical semantic drift; callers may still rely on old names.
