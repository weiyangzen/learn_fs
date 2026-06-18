# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/syslog.h

## Purpose
Defines syslog facility, priority, mask, and openlog option constants.

## Main Interfaces
- Facility constants:
  - `LOG_KERN`, `LOG_USER`, `LOG_MAIL`, `LOG_DAEMON`, `LOG_AUTH`, `LOG_SYSLOG`, `LOG_LPR`, `LOG_NEWS`, `LOG_UUCP`, cron/authpriv/FTP/NTP/audit/console/local facilities.
- Facility helpers:
  - `LOG_NFACILITIES`
  - `LOG_FACMASK`
- Priority constants:
  - `LOG_EMERG` through `LOG_DEBUG`
  - `LOG_PRIMASK`
- Mask helpers:
  - `LOG_MASK(pri)`
  - `LOG_UPTO(pri)`
- `openlog()` options:
  - `LOG_PID`, `LOG_CONS`, `LOG_ODELAY`, `LOG_NDELAY`, `LOG_NOWAIT`

## Dependencies And Relationships
Used by kernel and userland logging paths that need canonical syslog encoding values.

## Research Notes
This is a compatibility header with BSD/AT&T heritage. Numeric encodings are ABI and protocol relevant.
