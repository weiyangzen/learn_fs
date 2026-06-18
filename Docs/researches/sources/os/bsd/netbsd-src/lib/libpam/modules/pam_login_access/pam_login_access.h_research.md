# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/pam_login_access.h

Read completely: 39 lines.

This header declares the shared helper:

`int login_access(const char *, const char *);`

It is included by both the PAM wrapper and parser implementation.

Security/reliability notes: declaration-only file with no include guard, relying on simple single-prototype usage.
