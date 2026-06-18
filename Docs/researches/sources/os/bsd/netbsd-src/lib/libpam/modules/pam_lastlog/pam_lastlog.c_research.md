# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_lastlog/pam_lastlog.c

Read completely: 387 lines.

This session module records logins and logouts in `utmp`, `wtmp`, `utmpx`, `wtmpx`, `lastlog`, and `lastlogx`, depending on compile-time support. It also displays the previous login record unless silenced by `PAM_SILENT` or login class `hushlogin`.

`pam_sm_open_session` fetches `PAM_USER`, `PAM_RHOST`, `PAM_SOCKADDR`, `PAM_TTY`, and optional `PAM_NUSER`, strips `/dev/` from the tty, and records the session unless `no_nested` is set and a nested user exists. Option `no_fail` forces success even after failures.

`pam_sm_close_session` strips `/dev/` from `PAM_TTY` and logs logout records with `logoutx`/`logwtmpx` and `logout`/`logwtmp`, again respecting `no_nested`.

Helper functions build and write `utmpx`, `lastlogx`, `utmp`, and `lastlog` records; `domsg` reports the last login time, host, and line through PAM text info.

Security/reliability notes: many string copies use fixed-size legacy record fields and intentionally truncate. The legacy `lastlog` path seeks by `uid * sizeof(struct lastlog)`, so very large uids rely on `off_t` width and filesystem behavior.
