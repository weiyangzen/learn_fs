# File Research: sources/os/bsd/netbsd-src/lib/libresolv/dst_api.c

Read completely: 1058 lines.

Provides the legacy BIND DST API used by TSIG/DNSSEC-era resolver code. `dst_init()` initializes a global algorithm function table and reads `DSTKEYPATH`; this NetBSD build initializes HMAC-MD5 support while leaving hooks for RSA, DSA, SHA1 HMAC, and other historical algorithms.

The file allocates and manages `DST_KEY` objects, compares keys, signs and verifies incrementally through per-algorithm function pointers, converts between DNS KEY RDATA and internal key objects, and reads/writes public/private key files using `K<name>+<alg>+<id>.<suffix>` naming.

For TSIG use, `dst_buffer_to_key()` is the important path: it wraps raw shared-secret bytes in a `DST_KEY`, computes a DNS key id, and hands signing/verification to `hmac_link.c`. The file is global-state heavy, uses legacy file formats, and assumes callers respect fixed buffer sizes such as `RAW_KEY_SIZE`.
