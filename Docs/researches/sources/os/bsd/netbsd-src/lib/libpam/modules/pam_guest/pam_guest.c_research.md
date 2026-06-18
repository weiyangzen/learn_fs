# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_guest/pam_guest.c

Read completely: 120 lines.

This PAM authentication module grants access only when `PAM_USER` is in a comma-separated guest list. The `guests` option overrides the default list `guest`; `nopass` skips password retrieval; `pass_is_user` requires the authentication token to equal the username; and `pass_as_ruser` stores the password token as `PAM_RUSER`.

Core logic is in `lookup`, which scans exact comma-delimited tokens, and `pam_sm_authenticate`, which fetches the target user, evaluates guest membership, optionally checks the password token, sets `GUEST=<user>` in the PAM environment on success, and otherwise returns `PAM_AUTH_ERR`. `pam_sm_setcred` is a no-op success path.

Security/reliability notes: this is intentionally permissive for configured guest accounts. `pass_as_ruser` treats a password as a remote-user identity and should be used carefully in stacks that trust `PAM_RUSER`.
