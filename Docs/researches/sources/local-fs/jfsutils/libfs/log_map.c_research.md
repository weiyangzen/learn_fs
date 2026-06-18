# File Research: sources/local-fs/jfsutils/libfs/log_map.c

## Purpose
Implements the map-reconstruction side of JFS logredo: reads block/inode allocation maps into compact workspaces, applies replay-time state, rebuilds map summaries, and writes corrected imap/bmap pages back.

## Core Functions
- `initMaps(vol)`: initializes block map and fileset inode map by reading trusted map inodes and their xtrees.
- `bMapInit()`, `iMapInit()`: allocate workspace, discover map page offsets from xtree leaves, and read control pages.
- `bMapRead()`, `bMapWrite()`, `iMapRead()`, `iMapWrite()`: page I/O wrappers for allocation maps.
- `dMapGet()`, `iagGet()`: lazily load dmap/IAG pages and allocate compact bitmap/data records.
- `updateMaps()`: writes imap first, then bmap if bmap workspace allocation succeeded.
- `writeImap()`, `updateImapPage()`: rebuild IAG free lists, AG summaries, pmap/wmap state, inode counts, and inode extent state.
- `writeBmap()`, `updDmapPage()`: rebuild dmap summary trees, dmapctl hierarchy, aggregate free counts, AG free counts, max active AG, and preferred AG.
- `rXtree()`: follows the leftmost path of an xtree to the first leaf.
- `adjTree()` and `maxBud()`: rebuild buddy summary trees from leaf bitmap state.
- `bread()`: buffer-cache page reader with LRU/hash management and modified-buffer flushing.

## Key Data/Algorithms
- Uses `maptab[256]` to count zero/free bits in imap/dmap bytes.
- Uses `budtab[256]` to compute maximum binary buddy free-run size in bitmap words.
- Converts between disk blocks, dmap numbers, block-map page numbers, and allocation groups with macros such as `BLKTODMAPN`, `DMAPTOBMAPN`, and `BLKNOTOAG`.
- Treats map xtrees as trusted at logredo time because map xtree updates are journaled and sync-written at commit.
- If bmap workspace allocation fails, logredo can continue without rebuilding the bmap and leave full fsck to rebuild it later; imap allocation failure is fatal to this path.

## Dependencies
Uses global logredo state from `logredo.c` (`vopen`, buffer pool, allocation flags), device I/O, endian helpers, JFS dmap/imap/dinode/xtree formats, and fsck message logging.

## Notes
The file is recovery-critical and stateful. It mutates persistent map pages, interleaves CPU/disk endian conversion before writes, and depends heavily on global volume/buffer state. `iMapWrite()` reports write failures using `bmap_wsp[page_number].page_offset`, which appears suspicious for an imap write path and is worth review if maintaining this code.
