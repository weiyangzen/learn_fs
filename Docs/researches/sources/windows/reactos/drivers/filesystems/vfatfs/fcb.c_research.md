# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/fcb.c

Purpose: Manages VFAT file control blocks: allocation, destruction, path hashing, parent/child relationships, FCB cache lookup, root FCB creation, file-object attachment, directory searches, and path resolution.

Key routines:
- `vfatNameHash` computes case-insensitive hashes for Unicode path/name strings.
- `vfatSplitPathName` splits a full path into directory and file components.
- `vfatInitFcb`, `vfatNewFCB`, `vfatDestroyFCB`, and `vfatDestroyCCB` manage FCB/CCB memory, resources, file locks, names, and attributes pointers.
- `vfatGrabFCB` and `vfatReleaseFCB` maintain reference counts under `DirResource`, uninitialize cache maps when refcount drops to one, and recursively release parent FCBs when children are destroyed.
- `vfatAddFCBToTable`, `vfatDelFCBFromTable`, and `vfatGrabFCBFromTable` maintain the VCB hash table by full long path and, for normal FAT, short-name path.
- `vfatMakeFullName`, `vfatInitFCBFromDirEntry`, `vfatMakeFCBFromDirEntry`, `vfatUpdateFCB`, and `vfatSetFCBNewDirName` build/update FCB identity and metadata from directory entries.
- `vfatMakeRootFCB` and `vfatOpenRootFCB` create/cache the root FCB with FAT/FAT32/FATX-specific size and first-cluster state.
- `vfatAttachFCBToFileObject` attaches an FCB and fresh CCB to an opened file object.
- `vfatDirFindFile` scans a directory for long or short-name matches and creates an FCB for the found entry.
- `vfatGetFCBForFile` resolves absolute or parent-relative paths component by component, using the FCB hash table first and directory scans on misses.

Implementation notes:
- FCBs contain both full path strings and split `DirNameU`/`LongNameU`, plus `ShortNameU` where applicable.
- Directory FCB sizes are derived from root-directory sectors or by walking cluster chains.
- Parent-child relationships are tracked with `ParentListHead`/`ParentListEntry`; adding an FCB grabs its parent.
- Root FCB starts with refcount 2, initializes directory caching immediately, and is stored in `pVCB->RootFcb`.
- Path resolution normalizes casing/path spelling by replacing path components with the long names from cached or discovered FCBs.

Dependencies and interactions:
- Heavily used by create/open, directory enumeration, rename/move, cleanup/close, flush, and file-information paths.
- Depends on directory-entry scanning through `VfatGetNextDirEntry`, FAT-chain helpers for directory sizing, and cache initialization from `dirwr.c`.

Notable limitations and risks:
- `vfatInitFcb` bugchecks on path-buffer allocation failure rather than returning an error.
- Directory size calculation loops appear to call `NextCluster` with the first cluster rather than the current cluster in the shown implementation, which is worth reviewing against the expected helper signature.
