# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_lastlog/Makefile

Read completely: 38 lines.

This builds `pam_lastlog` from `pam_lastlog.c`, installs `pam_lastlog.8`, and defines `SUPPORT_UTMP`, `SUPPORT_UTMPX`, and `LOGIN_CAP`.

It links against `libutil` and suppresses string truncation warnings for `pam_lastlog.c`.

Security/reliability notes: build-only file. The compile flags enable both legacy `utmp` and newer `utmpx` session accounting paths.
