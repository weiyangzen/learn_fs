# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/crypt-argon2.c

Read completely: 442 lines.

Provides optional Argon2 support for `libcrypt` when `HAVE_ARGON2` is enabled. It supports `$argon2i$`, `$argon2d$`, and `$argon2id$` encodings, parses version and labeled parameters (`m=`, `t=`, `p=`), decodes the unpadded base64 salt, and calls `argon2_hash()` to generate the encoded output.

`estimate_argon2_params()` chooses default memory/time/threads based on `HW_USERMEM64`, `RLIMIT_AS`, and a roughly one-second trial hash loop. It bounds memory coarsely from small systems up to 32 MiB defaults and falls back to conservative values if probing/hash setup fails.

`decode_option()` is permissive about unknown top-level algorithm names, defaulting to Argon2id, but rejects unknown parameter labels. `__crypt_argon2()` uses fixed stack buffers for password, salt, raw hash, and encoded output, then returns a static 512-byte buffer. It wipes temporary buffers but prints Argon2 library failures to stderr, which is unusual for a libc hashing routine.
