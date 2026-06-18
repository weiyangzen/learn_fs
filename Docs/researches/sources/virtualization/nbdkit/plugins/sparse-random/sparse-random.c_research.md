# File Research: sources/virtualization/nbdkit/plugins/sparse-random/sparse-random.c

Implements a deterministic sparse virtual disk with configurable size, seed, block size, data percentage, expected data-run length, and random-content mode. It stores one bitmap bit per logical block to classify blocks as data or holes, defaulting to 4 KiB blocks and 10 percent data.

At get-ready time it constructs the bitmap using a two-state Markov-like process that alternates hole/data runs with probabilities chosen to approximate both target data percentage and average run length. Reads return zeroes for holes, a repeated nonzero byte per data block by default, or full deterministic random block contents when `random-content=true`.

Writes verify that supplied data exactly matches the generated content; trim and zero succeed only when the range covers holes and fail on data blocks. The plugin advertises multi-connection consistency, native no-op cache behavior, flush as a no-op, block-size hints, and extents that report holes as `HOLE|ZERO` and data as allocated.
