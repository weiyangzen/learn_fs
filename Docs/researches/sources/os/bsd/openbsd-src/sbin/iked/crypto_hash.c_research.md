# File Research: sources/os/bsd/openbsd-src/sbin/iked/crypto_hash.c

`crypto_hash.c` implements the NaCl-compatible `crypto_hash_sha512()` function declared in `crypto_api.h`. It delegates directly to OpenSSL `EVP_Digest()` with `EVP_sha512()`.

The function returns `0` on digest success and `-1` on OpenSSL failure. It is a small compatibility wrapper, not a higher-level iked crypto abstraction.
