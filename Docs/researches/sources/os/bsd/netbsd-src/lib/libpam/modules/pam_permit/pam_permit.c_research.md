# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_permit/pam_permit.c

Read completely: 99 lines.

This module implements all main PAM service hooks as unconditional success. `pam_sm_authenticate` first calls `pam_get_user` and propagates errors, but otherwise returns `PAM_SUCCESS`; setcred, account, password, open-session, and close-session hooks all return success.

Security/reliability notes: this module deliberately permits access and should only appear where the PAM stack is intentionally bypassing checks or providing a placeholder.
