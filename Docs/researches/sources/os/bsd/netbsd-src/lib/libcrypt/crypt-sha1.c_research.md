# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/crypt-sha1.c

Read completely: 189 lines.

Implements NetBSD’s `$sha1$` password hash using repeated HMAC-SHA1. The format is `$sha1$<iterations>$<salt>$<digest>`. If the salt lacks the magic prefix, it generates a randomized iteration count using `__crypt_sha1_iterations()`.

`__crypt_sha1_iterations()` treats the provided hint as a maximum-ish value and subtracts a random amount up to one quarter of it, reducing precomputed dictionary reuse. `__crypt_sha1()` builds the initial HMAC input from salt, magic string, and iteration count, then repeatedly HMACs the previous digest with the password as key.

The output digest is encoded using the library’s traditional crypt base64 via `__crypt_to64()`. It returns a static buffer and wipes the HMAC scratch buffer. Salt scanning is bounded by `CRYPT_SHA1_ITERATIONS` rather than the salt-length constant, but output storage effectively limits accepted salt size.
