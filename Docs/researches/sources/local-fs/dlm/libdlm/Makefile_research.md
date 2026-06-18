# File Research: sources/local-fs/dlm/libdlm/Makefile

## Purpose
Builds threaded and non-threaded DLM user libraries, pkg-config files, public headers, man pages, and udev rules.

## Build Products
- `libdlm.so.3.0` from `libdlm.c` with `_REENTRANT` and pthread support.
- `libdlm_lt.so.3.0` from the same source without `_REENTRANT`.
- `libdlm.pc` and `libdlm_lt.pc`.
- Public header `libdlm.h`.
- Man pages for lockspace, lock/unlock, dispatch, pthread, cleanup APIs.
- udev rules `51-dlm.rules`.

## Build Details
- Uses PIC and common hardening flags.
- Threaded library links with `-lpthread`; both use `-Wl,-z,now`.
- Installs symlinks for soname and unversioned shared library names.

## Risks / Gaps
- `LIBNUM=/lib64` is a platform assumption unless overridden.
- pkg-config files are generated with `cat | sed`, which is simple but less portable than install-time substitution tooling.
