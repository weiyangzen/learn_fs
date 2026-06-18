# sources/security-integrity/gocryptfs/contrib/findholes/holes/holes.go

Purpose: This package inspects sparse-file hole/data layout using `SEEK_DATA` and `SEEK_HOLE`.

Important APIs and functions: It defines `Segment`, `SegmentType`, `Whence`, string/pretty-print helpers, `Find(fd)` to discover alternating data/hole ranges, `Verify(fd, segments)` to validate seek behavior at every offset, and `Create(path)` to generate a sparse test file.

Control flow and state: `Find` starts by identifying whether offset zero is data or hole, then alternates `SEEK_HOLE` and `SEEK_DATA` until ENXIO signals no more data. `Create` writes bytes at random offsets and may truncate to force trailing holes.

Dependencies and integration points: Used by the contrib `findholes` CLI to test sparse-file behavior through gocryptfs mounts.

Risks and test signals: `SEEK_DATA` semantics vary across filesystems. `Verify` can be expensive because it checks each offset. Signals include coherent segment sequences ending in EOF and no seek-loop errors.
