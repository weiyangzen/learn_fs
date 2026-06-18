# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/pkp_hash.c

Small Pearson string hash implementation using a fixed 256-entry permutation table.

Key responsibilities:
- Defines `pkp_tab`, a 256-entry lookup table for Pearson hashing.
- Implements `pkp_tab_hash(char *str, int len)`, seeded from an arbitrary key plus input length.
- Iterates each input byte by table-indexing `(hash + str[i]) mod PKP_HASH_SIZE`.
- Returns a compact unsigned hash value in the table range.

Dependencies:
- Includes `sys/pkp_hash.h` for `PKP_HASH_SIZE` and public declaration.
- Assumes `PKP_HASH_SIZE` is a power of two because `MOD2()` masks rather than divides.

Notable risks:
- This is a fast non-cryptographic hash; it is suitable for table distribution, not adversarial integrity.
- Signed `char` input may affect indexing if callers pass bytes with the high bit set on platforms where `char` is signed.
- Table size and `MOD2()` must remain consistent.
