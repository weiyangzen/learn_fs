# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/write.c

Simple deterministic stdout data generator.

Key behavior:
- Fills a 1024-byte buffer with repeated 64-byte alphabet/digit pattern.
- Stores the current block offset high/low bytes into the first two bytes of each 64-byte chunk.
- Writes the 1024-byte buffer to stdout repeatedly.
- Default repeat count is 2560; optional first argument overrides it.

Use:
- Likely a test/load generator for pipes, devices, or file writes.

Filesystem relevance:
- Indirect test utility for write paths.
