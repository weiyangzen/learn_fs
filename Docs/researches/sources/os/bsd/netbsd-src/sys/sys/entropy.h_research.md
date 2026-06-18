# File Research: sources/os/bsd/netbsd-src/sys/sys/entropy.h

Declares kernel entropy subsystem interfaces.

Key content:
- Kernel-only header; user inclusion triggers an error.
- Includes libkern entropy pool definitions.
- `ENTROPY_CAPACITY` aliases `ENTPOOL_CAPACITY`.
- Extraction flags: `ENTROPY_WAIT`, `ENTROPY_SIG`, `ENTROPY_HARDFAIL`.
- APIs: boot request, reset, gather, consolidate, epoch, readiness query, extract, poll, kqfilter, ioctl.

Important behavior:
- Integrates random-device readiness, polling, kqueue, and ioctl paths.
- Header is intentionally not a public userland API.
