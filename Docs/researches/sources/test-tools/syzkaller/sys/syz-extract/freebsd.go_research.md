# sources/test-tools/syzkaller/sys/syz-extract/freebsd.go

Purpose: FreeBSD backend for constant extraction.

Important APIs/types/functions: `freebsd.prepare`, `freebsd.prepareArch`, and `freebsd.processFile`.

Control flow: requires `-build`, symlinks `machine` and `x86` include directories into the build dir, composes FreeBSD kernel include/compat flags, appends target C flags, and calls shared `extract` with ELF-section extraction and `<sys/syscall.h>`.

State and persistence: creates symlinks in the extraction build directory; no persistent output beyond central `.const` writing.

Dependencies and integration points: relies on FreeBSD source layout, clang/target compiler configuration from `sys/targets`, and shared `fetch.go`.

Risks: hard-coded compatibility defines need maintenance for FreeBSD release transitions. Symlink creation fails if paths already exist, so build dirs must be clean.

Test signals: no direct tests; extraction and generated sys build are the validation path.
