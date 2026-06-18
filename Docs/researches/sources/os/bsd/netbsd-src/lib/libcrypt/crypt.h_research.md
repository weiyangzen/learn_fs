# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/crypt.h

Read completely: 32 lines.

Private header for `libcrypt` internals. It marks internal functions with hidden ELF visibility through `crypt_private`, declares hash implementations, salt generators, utility encoders, and optional Argon2 entry points.

It defines `SHA1_MAGIC` as `$sha1$` and `SHA1_SIZE` as 20. This header ties together `crypt.c`, `pw_gensalt.c`, `crypt-sha1.c`, `hmac_sha1.c`, `md5crypt.c`, `bcrypt.c`, `util.c`, and optional Argon2 code without exporting these helper symbols as public ABI.
