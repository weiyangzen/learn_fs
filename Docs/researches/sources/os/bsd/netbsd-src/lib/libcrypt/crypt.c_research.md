# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/crypt.c

Read completely: 1095 lines.

Central `crypt(3)` implementation and legacy DES engine. `crypt()` calls private `__crypt()` and returns traditional failure sentinels `*0` or `*1` if hashing fails.

At the top level, `__crypt()` dispatches non-DES schemes by parsing the substring between leading `$` separators: `$2a$` to bcrypt, `$sha1$` to SHA1-HMAC, `$1$` to MD5 crypt, and optional `$argon2id$`, `$argon2i$`, or `$argon2d$` to Argon2. Unknown or malformed non-DES schemes fail.

The rest implements classic DES and extended DES. It builds a DES key from up to eight password characters, handles `_PASSWORD_EFMT1` extended DES with a 24-bit iteration count and 24-bit salt, and otherwise uses 25 iterations with a 12-bit salt. `des_setkey()`, `des_cipher()`, `setkey()`, and `encrypt()` provide compatibility DES APIs.

The DES implementation initializes permutation, key-schedule, S/P/E, and final-permutation tables lazily. State such as `KS`, `cryptresult`, and table readiness is static global state, so the classic API is not reentrant. The file also preserves historical invalid-salt behavior while rejecting passwd-format-unsafe salt characters.
