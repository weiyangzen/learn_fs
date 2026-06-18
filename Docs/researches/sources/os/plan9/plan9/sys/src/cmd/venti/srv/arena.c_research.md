# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/arena.c

Purpose: core Venti arena storage management.

Key responsibilities:
- Initialize existing arenas (`initarena`) from header/trailer and create new arenas (`newarena`).
- Read/write clump data and clump info directory entries.
- Allocate and append new clumps through `writeaclump`.
- Maintain arena memory/disk stats, sealing state, and checksums.
- Load clump-info-group (`cig`) summaries for index readahead and address grouping.

Major behavior:
- Arenas reserve one block for header and one for trailer; usable clump storage is `size - 2*blocksize`.
- `readarena`/`writearena` perform block-aligned partition I/O with bounds checks against clump storage and directory size.
- `writeaclump` seals the arena when a new clump plus directory metadata no longer fits, writes packed clump bytes, updates stats, writes clump info, and writes the trailer.
- `setatailstate` reconciles arena tail state through the main index map.
- `sealarena` queues background checksum work; `sumarena` computes a checksum across the arena with the trailer checksum field zeroed.
- `wbarena` writes the trailer; `wbarenahead` writes the header.
- `loadarena` validates trailer and compares header consistency.
- `loadcig`, `arenatog`, and `asumload` map arena offsets to clump groups and load index entries.

Integration points:
- Depends on server `dat.h`/`fns.h`, partition I/O, dirty block cache, clump pack/unpack, stats, index globals, and background `vtproc`.
- Used by broader Venti server read/write/index code.

Risks:
- Arena locking is central; writes hold `arena->lock`, while background checksum also updates arena state.
- `writearena` and `writeaclump` set `ok = 0` before `putdblock`; any async write failure is not captured here.
- `loadcig` may scan tens of megabytes of table-of-contents data on first access.
- Sealed arenas should be immutable except repairs; code relies on this invariant for checksumming and indexing.
