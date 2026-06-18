# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/hmac_sha1.c

Read completely: 20 lines.

Instantiates the generic `hmac.c` template for SHA1. It includes `<sha1.h>` and `crypt.h`, maps `HMAC_FUNC` to `__hmac_sha1`, sets `HASH_LENGTH` to `SHA1_DIGEST_LENGTH`, maps context and init/update/final macros to NetBSD SHA1 routines, and then includes `hmac.c`.

This file exists so the generic HMAC body can be compiled as a concrete hidden `libcrypt` helper for `crypt-sha1.c`.
