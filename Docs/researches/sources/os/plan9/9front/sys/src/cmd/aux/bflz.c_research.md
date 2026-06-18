# File Research: sources/os/plan9/9front/sys/src/cmd/aux/bflz.c

Role: Standalone brute-force Lempel-Ziv-like compressor with a custom `BLZ` output format.

Format:
- Output starts with `BLZ\n` and a 32-bit big-endian uncompressed length.
- Then a block stream follows: raw blocks are encoded with top bit set and length in lower 31 bits; reference blocks contain length and 32-bit source offset.
- Raw data bytes are accumulated separately and appended after the block descriptions.

Algorithm:
- Reads the entire input into memory, allocates output raw storage, then scans with a rolling hash over `win` bytes.
- Hash table maps rolling sums to `Node` entries that remember up to three prior offsets.
- Greedily emits a reference when the best previous run reaches `minrun`; otherwise emits raw bytes.
- Avoids pathological chains for long repeated-byte runs using `maxrle`.

Options:
- `-d` verbose tracing, `-s` same-byte replacement threshold, `-m` minimum distance, `-n` window size and minimum run.

Assumptions:
- Input and output reconstruction must fit in memory.
- It uses `#define malloc sbrk`, so memory behavior is intentionally simple and non-freeing.
