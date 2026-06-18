# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/md5.c

`md5.c` is the RSA Data Security, Inc. reference MD5 implementation bundled for the IPFilter test harness.

Contents:
- Standard MD5 context initialization (`MD5Init`).
- Incremental update logic (`MD5Update`) with 64-byte block processing and bit count tracking.
- Final padding, length append, digest serialization, and output copy (`MD5Final`).
- The four MD5 round functions/macros and a private `Transform()` routine with the standard constants and rotations.
- Kernel/user include split: includes `<sys/systm.h>` under `_KERNEL`, otherwise `<string.h>`.

Use in this group:
- `ipftest/ip_fil.c` uses this implementation to compute pseudo TCP initial sequence numbers for user-space test behavior.
- `md5.h` gates definitions to avoid conflicts with system MD5 headers.
