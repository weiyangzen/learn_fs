# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/des.c

- Role: Implements DES block encryption/decryption and key schedule generation for `u9fs` authentication support.
- Key functions: `block_cipher(expanded_key, text, decrypting)` runs 16 DES rounds over one 8-byte block; `key_setup(key, ek)` expands a 7-byte DES key into the 128-byte round-key table consumed by `block_cipher`.
- Data structures: Large static combined S/P-box tables (`s0p` through `s7p`), initial/final permutation helpers, and `keyexpand` bit-placement tables.
- Integration: Declared in `plan9.h`; used by authentication modules built into the u9fs makefile.
- Risks/notes: Uses `long` for bit operations, so portability depends on assumptions about width/sign behavior; DES itself is legacy cryptography and unsuitable for modern security except protocol compatibility.
