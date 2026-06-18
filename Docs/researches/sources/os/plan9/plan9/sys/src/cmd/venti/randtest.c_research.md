# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/randtest.c

Purpose: randomized Venti read/write throughput and integrity tester.

Behavior:
- Generates deterministic pseudo-random block contents from a seed and template.
- Can write, read, or both; default is both.
- Supports block size, total bytes, max blocks, random byte percentage, permuted order, host, concurrency, and disabling SHA1 double-check.
- `wr` computes expected SHA1 and writes a data block.
- `rd` recomputes expected score and verifies readback bytes.
- `run` emits blocks in sequential or permuted order, optionally dispatching to worker channels.
- Includes a Mitchell/Reeds-style pseudo-random generator (`xxxsrand`, `xxxlrand`).

Integration points:
- Uses Venti client APIs and Plan 9 thread channels.
- Useful for performance and integrity testing of Venti servers.

Risks:
- Concurrent mode starts both read and write workers; caller must choose operation flags appropriately.
- The first word of each generated block is overwritten with the block order value, so templates are not pure random bytes.
