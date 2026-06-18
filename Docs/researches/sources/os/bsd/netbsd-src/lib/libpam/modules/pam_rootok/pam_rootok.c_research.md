# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rootok/pam_rootok.c

Read completely: 78 lines.

This authentication module succeeds only when the real uid is 0. Non-root callers get a verbose refusal and `PAM_AUTH_ERR`. `pam_sm_setcred` returns success.

Security/reliability notes: it checks `getuid`, not effective uid, so setuid-root programs invoked by non-root users do not automatically pass.
