# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/mirrorarenas.c

Purpose: Mirrors one Venti arena partition to another, copying only data that has changed or is missing.

Key behavior:
- Opens source read-only and destination read/write, loads both arena partitions, and verifies matching arena count, version, block size, size, and name.
- `copy` overlaps reads and destination writes through a write thread and two 1 MiB buffers.
- `mirror` copies arena headers, new data, directory blocks, holes for sealed arenas, and trailer blocks as needed.
- For sealed arenas, it can compute/validate SHA1 across the destination and write the final seal score.
- `mirrormany` mirrors all arenas or a comma/range selection.

Dependencies:
- Uses Venti arena/partition metadata, `readpart`, `writepart`, arena pack/unpack helpers, SHA1, and Plan 9 thread channels.

Notable details:
- Refuses unsafe states such as destination sealed while source is unsealed, or source used size less than destination used size.
- `-F` forces full copy; `-s` disables SHA1 verification while mirroring sealed arenas.
