# File Research: sources/os/bsd/openbsd-src/sbin/mount/mntopts.h

`mntopts.h` defines the shared mount-option table format used by `getmntopts.c`. It provides option behavior flags, `struct mntopt`, `union mntval`, and macros for common user-visible mount options.

The common option macros cover async, noatime/accesstime, nodev, noexec, nosuid, noperm, wxallowed, rdonly/ro/rw, sync, quota placeholders, softdep, force, update, reload, and fstab compatibility flags such as `auto` and `net`.

`MOPT_STDOPTS` is the standard option set consumed by most filesystem-specific helpers. The header is a compatibility layer between text `-o` options and kernel `MNT_*` flags.
