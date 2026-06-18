# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/pam_login_access.c

Read completely: 106 lines.

This PAM account module applies `login_access()` to the current login attempt. It fetches `PAM_USER`, `PAM_RHOST`, and `PAM_TTY`; local logins are checked against the tty, while remote logins are checked against the remote host.

On a match allowing access it returns `PAM_SUCCESS`; otherwise it emits a verbose PAM error naming the denied user and tty/host, then returns `PAM_AUTH_ERR`.

Security/reliability notes: it calls `gethostname` into a local buffer but does not use the result. If `PAM_TTY` is null for a local login, it passes null through to `login_access`, whose string matching assumes non-null input.
