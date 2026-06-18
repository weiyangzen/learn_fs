# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/arena.c

Purpose: Implements Venti server arena lifecycle, clump data I/O, clump-directory access, arena sealing, checksumming, and clump-info group indexing.

Key behavior:
- `initarenasum` starts a background checksum worker for sealed arenas.
- `initarena` loads an arena from disk header/trailer, validates stats, and schedules sealing if needed.
- `newarena` creates a fresh arena with a valid header/trailer, randomized clump magic for newer versions, and an initial zero block.
- Reads and writes clump directory entries through `readclumpinfo`, `readclumpinfos`, and `writeclumpinfo`; directory blocks are stored in reverse order at the end of the arena.
- `readarena` and `writearena` perform bounded block-cache I/O inside the clump data region.
- `writeaclump` appends a packed clump, updates memory stats, compressed counts, clump info, clump-info group starts, timestamps, and arena trailer.
- `setatailstate` advances disk tail state across arenas in index order and seals arenas whose state becomes sealed.
- `backsumarena`, `sumproc`, and `sumarena` asynchronously compute and write SHA1 checksums for sealed arenas.
- `wbarena` and `wbarenahead` write trailer and header blocks.
- `loadarena` reads trailer/header metadata and logs inconsistencies between them.
- `okarena` validates basic size and count relationships.
- `loadcig`, `arenatog`, and `asumload` build and use clump-info-group offset tables for index-entry readahead.

Dependencies:
- Uses Venti server `dat.h`/`fns.h`, partition I/O, disk cache blocks, clump pack/unpack helpers, arena pack/unpack helpers, stats, tracing, scheduler hooks, SHA1, and global `mainindex`.

Notable details:
- Arena usable data excludes one header block before and one trailer block after the arena body.
- `writeaclump` seals the arena when the next clump plus directory growth would exceed arena size.
- Sealed arena checksums treat the checksum field itself as zero during SHA1 calculation.
