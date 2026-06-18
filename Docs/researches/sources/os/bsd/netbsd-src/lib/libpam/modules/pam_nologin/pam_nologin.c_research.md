# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_nologin/pam_nologin.c

Read completely: 158 lines.

This authentication module denies logins when a configured nologin file exists. It defaults to `/etc/nologin`, but login class capability `nologin` can override the path, and `ignorenologin` can bypass the check. Root defaults to bypass unless the login class overrides that default.

`pam_sm_authenticate` fetches the user, requires an existing passwd entry, obtains login class capabilities, opens the nologin file, prints its contents via `pam_error`, and denies authentication. Missing nologin file means success; other open failures deny login.

Security/reliability notes: the file is allocated based on `st_size` and read once without checking short read, so changing files can produce partial messages. The policy is fail-closed for existing-but-unreadable nologin files.
