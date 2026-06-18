# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/Makefile

## Purpose

This Makefile installs common kernel filesystem headers into the proto/root include tree and defines header standards-check targets for the `uts/common/fs` directory.

## File Shape

- Size: 63 lines, 1,556 bytes.
- SHA-256: `fdf4c485cfd98e3434b2710499166e3d81f052c460a45cc06cda8079410f865b`.
- Includes `../../../Makefile.master`.
- Installs `fs_subr.h` and `fs_reparse.h` into `$(ROOT)/usr/include/sys`.
- Installs `proc/prdata.h` into `$(ROOT)/usr/include/sys/proc`.

## Core Behavior

- Defines `ROOTDIR`, `ROOTDIRS`, `ROOTHDRS`, and `ROOTPROCHDRS`.
- Provides pattern install rules for top-level fs headers and `proc` headers using `$(INS.file)`.
- Defines `.check` rules using `$(DOT_H_CHECK)`.
- Enables `.KEEP_STATE` and parallel checking for `$(CHECKHDRS)`.
- `install_h` creates target include directories and installs headers.
- `check` runs standards checks over all listed headers.

## Maintenance Notes

This file is header-install plumbing, not filesystem runtime code. Add new exported headers here only when they are part of the installed system header surface; private implementation headers should remain out of `HDRS`/`PROCHDRS`.
