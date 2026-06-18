# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipftest/md5.h

`md5.h` declares the bundled RSA MD5 interface.

Key contents:
- License and provenance text for the RSA Data Security MD5 Message-Digest Algorithm.
- Include guard conditional on both `__MD5_INCLUDE__` and `_SYS_MD5_H`, preventing conflict with a system MD5 header.
- Defines `UINT4` as `unsigned int`.
- Defines `MD5_CTX` with bit counters, four-word buffer, 64-byte input buffer, and 16-byte digest.
- Declares `MD5Init`, `MD5Update`, and `MD5Final`.

This header is only support infrastructure for the local MD5 implementation used by the IPFilter test harness.
