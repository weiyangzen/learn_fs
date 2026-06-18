# File Research: sources/windows/reactos/drivers/filesystems/btrfs/create.c

Implements the WinBtrfs/ReactOS Btrfs create/open path: FCB and fileref allocation, path parsing, directory child lookup/materialization, inode-by-ID opens, file and stream creation, reparse handling, oplock/share-access checks, overwrite/supersede behavior, checksum preloading, removable-media verification, volume opens, and the `IRP_MJ_CREATE` dispatch entry point.

Key entry points:
- `drv_create()` is the IRP dispatcher. It handles opens of the filesystem device object, volume device object, raw volume file object, and normal file objects; verifies mounted/removable media state; acquires `load_lock`, `tree_lock`, and `fileref_lock`; runs `open_file()`; and completes or waits for pending oplock work.
- `open_file()` decodes create disposition/options, validates related file objects, handles `FILE_OPEN_BY_FILE_ID`, resolves paths and reparse stops, dispatches to open-existing or create-new logic, updates granted access, VPB, cache flags, and checksum loading.
- `open_file2()` enforces access checks, readonly/delete rules, reparse returns, directory-vs-file option compatibility, share access, and oplock checks before calling `open_file3()`.
- `open_file3()` finishes an existing-file open, including overwrite/supersede truncation, allocation extension, EA replacement/removal, stream deletion on overwrite, notifications, CCB setup, paging-file extent normalization, and open-count accounting.
- `file_create()` handles create-new requests after parent resolution. It parses final path components and alternate data stream names, processes atomic-create ECPs, performs parent access checks, and calls `file_create2()` or `create_stream()`.
- `file_create2()` creates a new regular file or directory: allocates inode/FCB/fileref, inherits permissions and compression/NOCOW flags, initializes security descriptor and EAs/LXSS metadata, optionally preallocates allocation size, inserts the FCB and directory child, marks dirty state, and sends notifications.
- `create_stream()` maps NTFS alternate data streams to Btrfs `user.*` xattrs, creates ADS FCBs/filerefs, checks reserved stream names, enforces write access on the owning object, and inserts stream entries into the parent FCB’s child list.

Path and object lookup:
- `split_path()` splits NT path components, detects stream syntax, strips `:$DATA`, rejects empty components, and represents each component as `name_bit`.
- `open_fileref()` walks absolute or related paths, strips leading root separators, optionally returns parent refs, tracks parsed offsets for reparses, and switches case sensitivity per directory/stream context.
- `open_fileref_child()` resolves one child component from a parent fileref. Normal entries use directory child hash lists; stream entries scan index-0 stream children and open ADS xattrs through `open_fcb_stream()`.
- `find_file_in_dir()` uses CRC32C hash buckets over original or upcased UTF-16 names to find `dir_child` entries and resolve subvolume root items.
- `open_fileref_by_inode()` supports file-id opens by reconstructing a fileref path from cached hardlinks, `INODE_REF`/`INODE_EXTREF`, `ROOT_BACKREF`, or the synthetic `$Root` directory.

FCB and directory state:
- `create_fcb()` allocates pageable/nonpageable FCB parts, initializes FSRTL headers, resources, locks, oplock state, extent/hardlink/xattr/dir-child lists, and starts the refcount at one.
- `create_fileref()` allocates a `file_ref`, initializes refcount and children list.
- `open_fcb()` loads an inode’s `INODE_ITEM`, infers Btrfs type when needed, reads hardlinks, xattrs, DOS attributes, NT security descriptor, compression/case-sensitive properties, extent data, directory children, file sizes, default attributes, and security descriptor inheritance. It then inserts the FCB into the subvolume cache/hash lists.
- `open_fcb_stream()` opens an ADS FCB backed by a `user.<stream>` xattr and computes the maximum remaining xattr payload room in the leaf.
- `load_dir_children()` materializes `TYPE_DIR_INDEX` entries into sorted/hash-indexed `dir_child` nodes and synthesizes `$Root` under the default subvolume when configured.
- `add_dir_child()` adds a newly created file/directory to the parent’s in-memory child index and hash lists.
- `inherit_mode()` carries parent Unix mode bits while clearing sticky/setuid and, for files, setgid.

Metadata and data helpers:
- `load_csum()` reads checksum items from the checksum tree across one or more `TYPE_EXTENT_CSUM` items.
- `fcb_load_csums()` lazily allocates and loads per-extent checksum buffers for regular extents unless the inode is NODATASUM.
- `file_create_parse_ea()` normalizes create-time EAs, folds duplicates, interprets LXSS `LXUID`, `LXGID`, `LXMOD`, and `LXDEV`, updates Unix inode fields/device type, and stores remaining EAs as the Btrfs EA xattr.
- `get_reparse_block()` converts Btrfs symlink data into a Windows `REPARSE_DATA_BUFFER`, validates file-backed reparse buffers, and copies directory reparse xattr buffers.
- `verify_vcb()` issues `IOCTL_STORAGE_CHECK_VERIFY` to removable backing devices and triggers `IoVerifyVolume()` when media change counts require it.
- `has_manage_volume_privilege()` records `SE_MANAGE_VOLUME_PRIVILEGE` on raw volume opens.

Important invariants:
- Name lookup depends on `dir_children_index`, `dir_children_hash`, `dir_children_hash_uc`, and 256-entry hash pointer arrays remaining sorted and synchronized.
- `tree_lock` protects Btrfs tree reads/mutations around create/open, while `fileref_lock`, per-FCB resources, and per-directory `dir_children_lock` protect object lifetime and directory child state.
- FCBs are cached per subvolume/inode and ADS FCBs are colocated near their owning inode in the FCB list.
- Filerefs represent path instances and carry parent/child links; directory FCBs may cache their primary fileref.
- Newly created objects are marked dirty before they are persisted; rollback lists are used around create/open work that mutates extents or metadata.
- Windows create dispositions must map to Btrfs mutations without violating image-section, share-access, oplock, readonly, subvolume-readonly, verity, and delete-pending constraints.
- Reparse handling must return both `STATUS_REPARSE` and the correct auxiliary buffer/tag so the I/O manager can continue path resolution.
- Alternate data streams are stored as xattrs and use index `0` directory-child entries, distinct from normal directory children whose indexes start at `2`.

Filesystem relevance:
- This file is the core namespace gateway for the driver. It bridges Windows create/open semantics to Btrfs inodes, subvolumes, xattrs, extents, checksums, security descriptors, reparse points, hardlinks, directory indexes, and file-id behavior.

Notable risks:
- `find_file_in_dir()` allocates an upcased string for case-insensitive lookup, then returns immediately on invalid filename without freeing it.
- In `file_create2()`, the case-insensitive duplicate check hashes `fpusuc` but compares `dc->name.Buffer` against `fpusuc.Buffer`; this appears to intend `dc->name_uc` and may miss collisions for differently cased names.
- In `open_fcb()`, an invalid copied NT security descriptor is freed without clearly nulling `fcb->sd`; later fallback security descriptor logic should be audited for stale-pointer assumptions.
- ADS handling notes a FIXME for xattr hash collisions; `open_fileref_child()` treats matching ADS hash as identity when selecting an existing ADS FCB.
- Create/open control flow is highly stateful: rollback, FCB insertion, fileref insertion, dirty marking, parent directory size changes, and share access must all stay paired across many failure paths.
- Reparse failure in `open_file2()` logs an error but converts it to success, which may hide malformed reparse metadata from callers.
