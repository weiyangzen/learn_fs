# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/cw.c

Core cached-WORM device implementation. It manages the cache map, cache states, WORM dump copy, filesystem dumps, recovery, cw reaming, read-only dump roots, and cw-specific console diagnostics.

Key data:
- `struct Cw` is private runtime state for a `Devcw`: cache/worm/ro devices, dump cursor, copy counters, traversal state, path name buffer, and dump recursion flags.
- Cache entry states persisted on disk:
  - `Cnone`, `Cdirty`, `Cdump`, `Cread`, `Cwrite`, `Cdump1`, `Cerror`.
- Opcodes passed to `cwio()`:
  - `Oread`, `Owrite`, `Ogrow`, `Odump`, `Orele`, `Ofree`, plus `Onone`.

Key responsibilities:
- `cwinit1()` allocates `Cw`, installs commands (`dump`, `statw`, `cwcmd`), installs `ro` flag, and initializes child devices.
- `cwinit()` validates cache map bucket tags and updates cache time/known WORM size.
- `cwio()` is the central state machine for reads, writes, allocation growth, dump marking, release, and free operations.
- `dumpblock()` copies one pending `Cdump` cache block to WORM, with retry/reread logic and `wmax` updates.
- `cwgrow()` extends filesystem size by `ADDFREE` blocks, marks new blocks dirty in cache, and adds them to the free list.
- `cwfree()` decides whether freed cw blocks can return to the freelist.
- `cacheinit()` lays out and initializes cache header and bucket map on cache device.
- `cwream()` initializes a fresh cw filesystem with cache header, superblock, cw root, ro root, and initial dump-marked blocks.
- `cwrecover()` scans WORM superblock chain and rebuilds cache metadata from the last good dump.
- `cfsdump()` performs a filesystem dump: recursively copies dirty live tree blocks, updates cw and ro roots, appends date-named dump entries, writes a new superblock, updates cache header, rewalks active fids, and extends locks by dump duration.
- `cwrecur()` recursively walks `Tsuper`, `Tdir`, and indirect blocks to split dirty/written blocks into immutable dump blocks.
- `rewalk()`/`rewalk1()`/`rewalk2()` update active `File.addr` paths after dump root relocation.
- `roread()` reads from cache if the block is dump/read state, otherwise from WORM.
- Diagnostic/maintenance commands under `cmd_cwcmd()` include `mvstate`, `prchain`, `searchtag`, `touchsb`, `savecache`, `loadcache`, `morecache`, `blockcmp`, `startdump`, `allflag`, `storesb`, `acct`, `clearacct`, and `test`.

Important interactions:
- Depends heavily on `Cache`, `Bucket`, `Centry`, `Superb`, `Dentry`, `Wpath`, and tags from `portdat.h`.
- Uses generic block/device operations from `sub.c`.
- Uses directory traversal/allocation from `dentry.c`.
- Uses console helpers for `/adm/cache` save/load.
- `wormcopy()` in `main.c` repeatedly invokes `dumpblock()` for each cw filesystem.

Research notes:
- `oldcachefmt` changes cache-data address calculation; `-c` in `main.c` sets it to 0 for the newer layout.
- `Cdump1` is a fallback state when write-induced dump preservation fails.
- `isdirty()` treats indirect blocks conservatively: any cached non-`Cnone` indirect block may force recursion.
- `cfsdump()` writes both partial and final super/cache updates; it uses `Bimm` to force critical metadata writes.
- `storesb()` is a specialized repair helper with a hard-coded default block number (`4168344`) and sanity relationship checks.
