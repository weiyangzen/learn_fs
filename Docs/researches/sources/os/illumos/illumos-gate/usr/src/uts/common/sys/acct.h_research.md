# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/acct.h

## Purpose

`acct.h` defines legacy process accounting record formats and accounting flags.

## Main Types

`comp_t` is a compact accounting “floating point” type with a 13-bit fraction and 3-bit exponent.

`struct acct` is the SVR4 accounting record with flags, exit status, uid/gid, controlling tty, start time, user/system/elapsed time, memory use, I/O counts, read/write block counts, and an 8-byte command name.

`struct o_acct` preserves the older SVR3 layout using old uid/gid/device types.

## Interfaces and Flags

Userland sees `acct(const char *)`. Kernel builds see `acct(char)`, `sysacct(char *)`, and `acct_fs_in_use(struct vnode *)`.

Flags include `AFORK`, `ASU`, `AEXPND`, and `ACCTF`.

## Research Notes

This is an ABI compatibility header for classic process accounting. Filesystem relevance appears in `acct_fs_in_use()`, which lets kernel code detect accounting files on vnodes/filesystems.
