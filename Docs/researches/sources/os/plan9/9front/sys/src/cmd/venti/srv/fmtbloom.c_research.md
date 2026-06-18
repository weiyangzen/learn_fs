# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/fmtbloom.c

Formats a Bloom filter partition/file.

Key behavior:
- CLI supports `-s size`, `-n nblocks`, and `-N nhash`.
- Defaults to full partition size and max hash count unless block count drives sizing.
- Enforces minimum 1 MiB, caps to `MaxBloomSize`, rounds down to a power of two, and may shrink if bits per block are excessive.
- Chooses near-optimal hash count as roughly `0.7 * bits-per-block`, capped at `BloomMaxHash`.
- Initializes Bloom header/data and writes it to disk.

Interactions:
- Uses `bloominit` and `writebloom`.

Notable details:
- Prints warnings when only part of the file/partition is used.
