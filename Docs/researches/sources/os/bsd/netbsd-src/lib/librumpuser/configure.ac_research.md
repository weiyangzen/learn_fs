# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/configure.ac

## Summary
Autoconf input defining POSIX rumpuser portability probes.

## Key Details
- Initializes package `rumpuser-posix` version `999` with bug reports to the rumpkernel GitHub URL.
- Generates `rumpuser_config.h`, uses `build-aux`, and declares C as the language.
- Requests large-file support and canonical target detection.
- Checks headers, types, functions, libraries, and structure members needed by the portable rumpuser implementation.
- Uses custom compile tests under `-Werror` for `sys/cdefs.h`, `pthread_setname_np` signatures, and `ioctl` command-argument type.
- Notes regeneration steps: run `autoreconf -iv`, update `rumpuser_port.h`, remove `autom4te.cache`, then commit/pull up.

## Notes
This file explains why `rumpuser_port.h` embeds NetBSD-default generated values while non-NetBSD/buildrump users can include a generated `rumpuser_config.h`.
