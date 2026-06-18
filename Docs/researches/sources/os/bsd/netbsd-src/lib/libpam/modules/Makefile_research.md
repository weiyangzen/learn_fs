# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/Makefile

Dynamic PAM module directory makefile. It lists core modules and conditionally adds S/Key and Kerberos modules based on `MKSKEY` and `MKKERBEROS`, then always adds `pam_ssh`.

The final include of `bsd.subdir.mk` drives subdirectory builds.
