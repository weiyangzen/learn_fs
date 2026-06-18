<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/Makefile.am -->
# sources/user-network-fs/nfs-utils/utils/nfsdcltrack/Makefile.am

## Purpose

`nfsdcltrack/Makefile.am` builds the older `nfsdcltrack` kernel usermode-helper client tracking program.

## Important APIs, types, and functions

It optionally installs under `/sbin` when `CONFIG_SBIN_OVERRIDE` is true because the kernel knows that helper path. It builds `nfsdcltrack` from `nfsdcltrack.c` and `sqlite.c`, installs the manpage, declares `sqlite.h`, defines `_LARGEFILE64_SOURCE`, and links support NFS, sqlite, and libcap.

## Control flow

Automake turns the declarations into build/install rules. There are no custom post-install hooks beyond the conditional `sbindir` override.

## State and persistence behavior

The Makefile has no runtime state. The built helper manages SQLite state at runtime.

## Dependencies and integration points

The `/sbin` override is an integration point with kernel helper invocation. Libraries match helper needs: sqlite for storage and libcap for privilege reduction.

## Risks and edge cases

Installing outside the path expected by older kernels breaks upcalls. Conditional automake syntax is deliberately written to avoid automake disabling the override, so refactors should be cautious.

## Test signals

Build/install tests should verify install location with `CONFIG_SBIN_OVERRIDE` true/false, link dependencies, manpage distribution, and helper availability at the configured kernel path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/nfsdcltrack/Makefile.am -->
