# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_skey/pam_skey.c

Read completely: 110 lines.

This authentication module validates S/Key one-time passwords. It uses `PAM_OPT_AUTH_AS_SELF` to authenticate `getlogin()` instead of `PAM_USER`, checks that the user has S/Key state, retrieves challenge text with `skey_keyinfo`, prompts as `Password [ <challenge> ]:`, duplicates the response, and calls `skey_passcheck`.

`pam_sm_setcred` is a no-op success path.

Security/reliability notes: if `getlogin()` returns null under `auth_as_self`, the code passes null into S/Key functions. The response is freed but not explicitly zeroed before free.
