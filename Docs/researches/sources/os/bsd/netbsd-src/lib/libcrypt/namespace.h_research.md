# File Research: sources/os/bsd/netbsd-src/lib/libcrypt/namespace.h

Read completely: 94 lines.

Force-included namespace isolation header for `libcrypt`. It remaps imported Argon2, BLAKE2b, Argon2 core/encoding/ref helper symbols, `estimate_argon2_params`, and `getnum` to `__libcrypt_internal_*` names.

This prevents bundled Argon2 implementation symbols from leaking into or conflicting with the public process symbol namespace when `libcrypt` is linked. It is build infrastructure rather than runtime logic, but it is important for ABI cleanliness and avoiding clashes with external Argon2/BLAKE2 libraries.
