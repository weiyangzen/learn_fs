# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_securetty/pam_securetty.c

Read completely: 125 lines.

This PAM account module restricts root logins to secure terminals. It gets the user and passwd entry, immediately succeeds for non-root users, fetches `PAM_TTY`, strips a `/dev/` prefix, and checks `getttynam` for `TTY_SECURE`.

If root is not on a secure tty, it logs a notice including `PAM_RHOST` when available, emits “Not on secure TTY”, and returns `PAM_AUTH_ERR`.

Security/reliability notes: only root is subject to this check. It logs `(const char *)tty` even if tty is null in the refusal path, depending on syslog printf behavior.
