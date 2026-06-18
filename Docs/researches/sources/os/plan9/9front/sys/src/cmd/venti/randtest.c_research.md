# File Research: sources/os/plan9/9front/sys/src/cmd/venti/randtest.c

Purpose: Venti read/write throughput and integrity test using deterministic pseudo-random data.

Key behavior:
- Generates blocks from a template seeded by a custom PRNG, with each block tagged by its order index.
- Writes blocks to Venti and optionally double-checks returned scores against locally computed SHA1.
- Reads blocks back by recomputing their scores and verifies byte-for-byte data.
- Supports configurable block size, total bytes, max blocks, seed, randomness percentage, permutation, read/write selection, concurrency, host, and disabling double SHA1 checks.
- Reports MB/s for write and read phases.

Dependencies:
- Uses Venti read/write APIs, SHA1, Plan 9 threads/channels, and a Mitchell-Reeds style PRNG.

Notable details:
- Multi-thread mode starts both read and write worker pools and feeds block buffers over channels.
