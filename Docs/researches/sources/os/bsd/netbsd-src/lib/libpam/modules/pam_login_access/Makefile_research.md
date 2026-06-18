# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_login_access/Makefile

Read completely: 32 lines.

This builds `pam_login_access` from `pam_login_access.c` and `login_access.c`, and installs `pam_login_access.8` plus `login.access.5`.

It uses the shared PAM module make rules.

Security/reliability notes: build-only file. It ties the PAM account module to the local `/etc/login.access` parser.
