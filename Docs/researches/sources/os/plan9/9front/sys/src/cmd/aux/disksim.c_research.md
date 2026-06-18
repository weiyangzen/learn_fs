# File Research: sources/os/plan9/9front/sys/src/cmd/aux/disksim.c

Role: 9P disk simulator presenting an sd-like directory with partition files.

Filesystem model:
- Mounts by default at `/dev` and exposes a top directory named like `sdXX`, containing `ctl` and partition files.
- Starts with a `data` partition covering the configured disk size once geometry is supplied.
- `ctl` supports `part name start end`, `delpart name`, `inquiry text`, and `geometry nsect sectsize c h s`.

Storage model:
- Uses sparse, demand-allocated 8192-byte blocks addressed through triple/double/indirect structures.
- If `-f file` is supplied, blocks are loaded from and dirtied back to that file; `-r` opens read-only.
- Reads from unallocated regions return a static zero block; writes of all-zero data can avoid allocation.

9P operations:
- Implements attach, walk, open, stat, read, and write through lib9p `Srv`.
- Partition reads and writes validate bounds, clamp counts at partition length, and handle unaligned fringe blocks.

Important details:
- `fsstat` and directory generators synthesize ownership as `disksim`.
- Partition qid versions change on partition recreation to detect stale fids.
