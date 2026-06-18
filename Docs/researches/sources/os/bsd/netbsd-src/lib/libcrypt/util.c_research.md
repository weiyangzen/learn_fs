# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/util.c

Read completely: 91 lines.

Shared `libcrypt` utility helpers. `getnum()` parses an unsigned long with `strtoul()`, accepting `NULL` as zero, rejecting empty or trailing-junk input, and propagating range errors. It stores the result as `size_t`.

`__crypt_to64()` encodes low-order six-bit groups with the traditional crypt alphabet `./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`. `__crypt_tobase64()` does the same with the standard base64 alphabet used by Argon2 salts.

These helpers are used by salt generators and hash encoders. They append exactly `n` characters and do not NUL-terminate; callers own buffer sizing and terminators.
