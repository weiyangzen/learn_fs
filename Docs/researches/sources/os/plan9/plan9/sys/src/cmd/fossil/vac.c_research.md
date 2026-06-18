# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/vac.c

This file implements Fossil directory metadata serialization, not the standalone `vac` archiver command. It packs/unpacks `MetaBlock`, `MetaEntry`, and `DirEntry` records using big-endian integer macros and Venti/Fossil allocation helpers.

`mbUnpack`, `mbPack`, `mbInsert`, `mbDelete`, `mbResize`, `mbAlloc`, and compaction helpers manage metadata block layout: header, index table, entry payloads, free space, holes, and legacy `MetaMagic-1` “botch” ordering.

`deSize`, `dePack`, and `deUnpack` encode/decode versioned directory entries including element name, data/meta entry references and generations, qid, uid/gid/mid, times, mode, and optional Plan 9/qid-space records. Versions 7 through 9 are accepted, with compatibility behavior for older fields.

Notable behavior: `mbSearch` supports both current and old broken prefix comparison order through `mb->botch`, preserving lookup compatibility with old on-disk metadata.
