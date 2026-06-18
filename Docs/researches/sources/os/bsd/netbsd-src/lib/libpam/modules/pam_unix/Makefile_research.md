# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_unix/Makefile

Read completely: 56 lines.

This builds `pam_unix` from `pam_unix.c`, installs `pam_unix.8`, and links against `libutil` and `libcrypt`. When `USE_YP` is not `no`, it defines `YP` and links `librpcsvc`.

It disables lint/profile/PIC archive installation and uses the common PAM module rules.

Security/reliability notes: build-only file. The `YP` conditional compiles NIS password-change support into the module.
