# File Research: sources/os/bsd/freebsd-src/sbin/savecore/Makefile

## Summary
Builds the `savecore` runtime utility and installs the default crash-directory `minfree` configuration.

## Main Elements
- Sets `PACKAGE=runtime`.
- Installs `minfree` under `/var/crash` with mode `0750`.
- Builds `PROG=savecore` and `savecore.8`.
- Links `libxo`, `zlib`, and `zstd`.
- Adds zstd include path from the kernel contrib tree.
- Conditionally enables Casper/fileargs/syslog support.
- Enables the `tests` subdirectory when `MK_TESTS` is on.

## Dependencies And Integration
Uses `bsd.prog.mk`, `src.opts.mk`, libxo, compression libraries, and optional Casper capability libraries.
