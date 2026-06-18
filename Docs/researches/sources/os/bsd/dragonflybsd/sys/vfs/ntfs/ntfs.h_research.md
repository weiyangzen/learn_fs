# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs.h

This is the main on-disk NTFS format and mount-state header. It defines cluster and Unicode types (`cn_t`, `wchar`), packed on-disk structures for boot sectors, file records, attributes, standard time fields, file-name attributes, index roots, index allocation records, index entries, attribute-list records, and `$AttrDef` records.

It also defines NTFS system inode numbers such as `$MFT`, `$Volume`, `$AttrDef`, root, `$Bitmap`, boot, bad-clusters, and `$UpCase`, plus attribute type IDs such as standard information, attribute list, file name, volume name, data, index root, index allocation, and index bitmap.

`struct ntfsmount` stores per-mount state: mount pointer, bootfile copy, device vnode/device, retained system vnodes, MFT record sizing, default uid/gid/mode, mount flags, free cluster count, translated attribute definitions, export state, character conversion tables, and iconv handles.

Important macros map between mount/vnode/fnode/ntnode objects (`VFSTONTFS`, `VTOF`, `VTONT`, `FTOV`, `FTONT`) and convert clusters, bytes, blocks, and disk offsets using the in-scope `ntmp`.

Research notes: the header uses `#pragma pack(1)` for disk structures, so layout is ABI-critical. Several comments mark fields as unknown or inferred, reflecting the age of this NTFS implementation.
