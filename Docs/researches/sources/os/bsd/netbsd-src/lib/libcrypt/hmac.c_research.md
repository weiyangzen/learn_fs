# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/hmac.c

Read completely: 309 lines.

Generic macro-parametrized HMAC implementation based on RFC 2104. It expects the including file to define `HMAC_FUNC`, `HASH_LENGTH`, `HASH_CTX`, `HASH_Init`, `HASH_Update`, and `HASH_Final`. In this library it is included by `hmac_sha1.c` to produce `__hmac_sha1()`.

The core function hashes oversized keys down to digest length, builds inner and outer pads using `0x36` and `0x5c`, computes `HASH(K xor ipad, text)`, then computes `HASH(K xor opad, inner_digest)` into the caller’s digest buffer.

Under `MAIN` or `UNIT_TEST`, it also includes hex conversion helpers, RFC 2202-style known-answer tests, and a small command-line driver. The production function does not explicitly wipe pad/key scratch buffers.
