# File Research: sources/os/bsd/dragonflybsd/sys/sys/syslog.h

Syslog priority, facility, option, and userland API definitions.

Key contents:
- Defines log socket paths:
  - `/var/run/log`
  - `/var/run/logpriv`
  - legacy `/dev/log`
- Defines priorities `LOG_EMERG` through `LOG_DEBUG`.
- Defines facility constants `LOG_KERN`, `LOG_USER`, `LOG_DAEMON`, `LOG_AUTHPRIV`, `LOG_LOCAL0` through `LOG_LOCAL7`, etc.
- Provides encoding helpers:
  - `LOG_PRI`
  - `LOG_MAKEPRI`
  - `LOG_FAC`
  - `LOG_MASK`
  - `LOG_UPTO`
- Under `SYSLOG_NAMES`, defines name-to-code arrays for priorities and facilities.
- Defines `openlog` option flags.
- Userland declarations:
  - `closelog`
  - `openlog`
  - `setlogmask`
  - `syslog`
  - `vsyslog`

Important behavior:
- Priority uses low 3 bits; facility is shifted left by 3.
- `LOG_PRINTF` is kernel-only pseudo-priority for `kprintf` behavior.
- Some historical priority names are kept as deprecated aliases.

Research notes:
- This is both libc API and kernel logging vocabulary.
- Facility/priority encodings must stay compatible with `syslogd`.
