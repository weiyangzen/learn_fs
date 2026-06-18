# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/md5crypt.c

Read completely: 148 lines.

Implements Poul-Henning Kamp’s MD5 password hash for `$1$` salts. `__md5crypt()` strips the `$1$` prefix if present, truncates salt at the first `$` or eight characters, and performs the standard MD5-crypt mixing sequence of password, magic, salt, alternate digest, and 1000 strengthening rounds.

The final 16-byte MD5 digest is rearranged into the traditional MD5-crypt base64 order and encoded with `__crypt_to64()`. It returns a static 120-byte password buffer and wipes the final digest before returning.

This is compatibility code for an old password hash. It is not thread-safe because of static storage and is cryptographically obsolete compared with bcrypt/Argon2.
