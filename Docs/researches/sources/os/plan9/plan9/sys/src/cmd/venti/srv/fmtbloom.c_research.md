# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/fmtbloom.c

Implements `fmtbloom`, which creates a Bloom filter partition/file. It chooses a power-of-two byte size, caps at `MaxBloomSize`, requires at least 1 MiB, and computes hash count from either explicit `-N` or expected block count `-n`.

When `-n` is supplied, it avoids using more bits than useful and chooses roughly `ln(2)` times the bits per block, capped at `BloomMaxHash`. Without explicit sizing, it uses the part size.

The command initializes the Bloom header/data with `bloominit()`, sets `nhash`, allocates zeroed data, attaches the target `Part`, and writes it with `writebloom()`.
