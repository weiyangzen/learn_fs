# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_rhosts/pam_rhosts.c

Read completely: 103 lines.

This module authenticates using classic rhosts trust. It gets the target user, verifies the user exists, denies root unless `allow_root` is configured, fetches `PAM_RUSER` and `PAM_RHOST`, then calls `ruserok`.

`pam_sm_setcred` is a no-op success path.

Security/reliability notes: rhosts trust is host/user-name based and generally weak by modern standards. The module prevents root use by default, but `allow_root` re-enables that risk.
