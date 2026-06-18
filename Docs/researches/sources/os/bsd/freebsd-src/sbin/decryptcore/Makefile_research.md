# File Research: sources/os/bsd/freebsd-src/sbin/decryptcore/Makefile

## Purpose
Builds the `decryptcore` encrypted kernel core dump decryptor.

## Main Elements
- `PROG=decryptcore`
- Sets `OPENSSL_API_COMPAT=0x10100000L`
- `LIBADD=crypto pjdlog`
- `MAN=decryptcore.8`
- Adds include path for `libpjdlog`.

## Dependencies And Integration
Links OpenSSL crypto and FreeBSD `pjdlog`.
