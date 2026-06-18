# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/dump.c

Implements incremental “dump CD” state, deduplication, and dump-tree reconstruction.

Deduplication uses `Dumpdir` nodes in two binary trees: one keyed by MD5 digest and one by block number. `md5cd`, `addfile`, `insertmd5`, and `lookupmd5` scan existing image file data so new files can reuse blocks when content matches.

`readkids` parses on-disc directory blocks into child `Direc` arrays, and `adddir` recursively scans existing trees into the dump index. `dumpcd` seeds a `Dump` from existing dump roots. `freekids` releases temporary child arrays.

Dump directory names are year/day paths. `adddumpdir`, `createdumpdir`, `rmdumpdir`, and `copybutname` maintain in-memory dump roots. `Cputdumpblock` writes a magic dump header block; `hasdump` finds such a block in descriptor sectors. `readdumpdirs` follows the linked dump-header chain to reconstruct dump root directories and root block/length pairs. `readdumpconform` follows the same chain to rebuild `_conform.map`.

Integration points: central to `dump9660.c` incremental mode and `write.c` content deduplication.

Risks and notes: dump headers are plain text inside 2048-byte blocks with strict field expectations. MD5 collisions are not handled beyond a duplicate warning. Some tree walks are unbalanced binary trees, not self-balancing.
