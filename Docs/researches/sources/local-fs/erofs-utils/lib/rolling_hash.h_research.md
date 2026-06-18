# File Research: sources/local-fs/erofs-utils/lib/rolling_hash.h

This header implements a simple Rabin-Karp-style rolling hash.

Constants:
- `PRIME_NUMBER` is `4294967295LL`.
- `RADIX` is 256.

Functions:
- `erofs_rolling_hash_init(u8 *input, int len, bool backwards)` computes an initial hash forward or backward across a window.
- `erofs_rolling_hash_advance(long long old_hash, unsigned long long RM, u8 to_remove, u8 to_add)` removes the outgoing byte contribution, multiplies by radix, adds the new byte, and normalizes negative results.
- `erofs_rollinghash_calc_rm(int window_size)` computes `RADIX^(window_size - 1) mod PRIME_NUMBER`.

Important note:
- The comment explicitly keeps signed `long long` for hashes because intermediate values may be negative before normalization.

Likely role:
- Used by dedupe/fragment matching code outside this group.
