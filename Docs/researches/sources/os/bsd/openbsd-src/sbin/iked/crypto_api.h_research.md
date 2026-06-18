# File Research: sources/os/bsd/openbsd-src/sbin/iked/crypto_api.h

`crypto_api.h` provides a small NaCl-compatible crypto API surface used by the DH/KEM code. It defines integer aliases, random-byte macros backed by `arc4random_buf()`/`arc4random()`, SHA512 hash size, constant-time verify declaration, and SNTRUP761 KEM sizes/functions.

The header is specifically needed for the hybrid SNTRUP761+X25519 group in `dh.c`. It declares public key, secret key, ciphertext, shared-secret sizes and KEM keypair/encapsulation/decapsulation routines.

It is not a general daemon header; it is a compatibility shim for imported/public-domain crypto routines.
