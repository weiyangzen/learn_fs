# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/olefs.c

Read-only 9P filesystem for Microsoft OLE Compound File Binary Format documents. It parses the compound file block allocation tables and directory tree, then exposes streams/storages as a mounted Plan 9 file tree.

Core structures:
- `Ofile`: backing `Biobuf`, number of FAT blocks, big-block map, root block, small-block map start.
- `Odir`: parsed directory entry with UTF-16 name, type, tree links, stream start block, and stream size.

Core behavior:
- Validates OLE magic `D0 CF 11 E0 A1 B1 1A E1`.
- Reads depot/FAT blocks from the header and extended depot chain.
- Reads directory entries from the root chain.
- Supports big streams through normal block chains and small streams via the root small-block depot.
- Builds a synthetic 9P tree with sanitized names, replacing spaces with `␣` and unsafe/control runes with `:`.
- Serves stream contents from `oleread()`.

Important functions:
- `oleopen()` parses the header and block map.
- `oreadblock()`, `oreadchain()`, `oreadfile()` implement block-chain reads.
- `convM2OD()` decodes on-disk OLE directory entries.
- `filldir()` recursively converts OLE storage tree entries into lib9p `File` objects.
- `main()` mounts the filesystem at `/mnt/doc` or `-m mtpt`.

Dependencies and integration:
- Uses Plan 9 `bio`, `thread`, and `<9p.h>`.
- Exposes a `Srv` with `.read = oleread`.

Notable risks:
- Complex OLE formats are only partially supported; timestamps are explicitly marked as a BUG.
- Recursion guard is a hardcoded depth limit of 100.
- `runestrecpy(rbuf, rbuf+sizeof rbuf, ...)` uses byte-size arithmetic on a Rune array, which is suspicious in modern terms.
- Several parse failures print diagnostics rather than returning structured errors.
