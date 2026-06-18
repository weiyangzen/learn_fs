# sources/test-tools/pynfs/nfs4.1/fs.py

## Purpose
`fs.py` implements the NFSv4.1 test server's filesystem object model. It provides in-memory and disk-backed filesystems, filesystem objects with NFS attributes and locking hooks, a `/config` pseudo-filesystem, and pNFS block/file layout filesystems that coordinate with data servers.

## Important APIs, Types, And Functions
- `MetaData` holds persistent object metadata: change counter, type, refcount, create verifier, owner, mode, timestamps, parent ID, symlink target, and device data.
- `FSObject` models one NFS object. It exposes NFS attributes as `fattr4_*` properties, stores metadata through `MetaData`, owns a `FileState`, a read/write lock, a seek lock, file/directory contents, layout state, and mount-covering pointers.
- Core `FSObject` APIs include `read`, `write`, `sync`, `close`, `set_attrs`, `lookup`, `lookup_parent`, `link`, `unlink`, `readdir`, `create`, `get_layout`, and `commit_layout`.
- `FileSystem` is the base filesystem with fsid, active-object cache, disk lock, root object, supported attributes, mount handling, object allocation, lookup, creation, sync, delegation options, layout options, and device-list hooks.
- `RootFS` is a read-only root filesystem; `StubFS_Mem` is volatile memory-backed; `StubFS_Disk` persists metadata and data files under a shelve-backed directory.
- `ConfigObj` and `ConfigFS` expose server, client, operation, and action config lines as read/write files under a synthetic config tree.
- `LayoutFSObj`, `BlockLayoutFS`, `FSLayoutFSObj`, `FileLayoutFS`, `FileLayoutFile`, and `FilelayoutVolWrapper` implement pNFS block-layout and file-layout behavior.
- `Device`, `my_ro_extent`, `my_rw_extent`, and `test_layout_dict` provide backing layout metadata for test layouts.

## Control Flow
`FileSystem.__init__` initializes supported attrs, an object cache, mount state, and a root directory created through `create`. `create` checks read-only state, allocates an ID, constructs the configured object class, and inserts it into `_ids`. `find` returns cached objects or calls `find_on_disk` under `_disk_lock`.

`FSObject.__init__` either wraps existing `MetaData` loaded from disk or creates fresh metadata from an NFS kind/createtype. It initializes regular-file storage with `init_file`, directory entries, directory cache, `FileState`, locks, layout state, and subclass hooks. `__getattr__` and `__setattr__` forward metadata fields to `self.meta`, so object attributes and persisted metadata share the same access surface.

Read/write/truncate flows acquire `seek_lock`, perform file-object operations, and bump the change counter. Attribute setting iterates the incoming bitmap dict, verifies server support and writeability via `nfs4lib.attr_info`, chooses either object or metadata target, sets values, returns the successfully-set bitmask, and records partial success in `NFS4Error.attrs` on failure.

Directory flow uses `entries` as a name-to-object-ID map. `lookup` checks access, resolves the ID, and follows mount overlays through `covered_by`. `lookup_parent` climbs to the mounted-on object when at a filesystem root. `create` allocates an object, defaults owner to the principal name, sets attrs, and links it into the parent. `readdir` caches name/object lists under timestamp verifiers and rejects unknown nonzero verifiers.

Config flow dynamically computes directory entries from encoded IDs. File objects associated with config lines reset their content to a comment plus current value. On close, dirty config files parse one non-comment line, assign through `ConfigLine.value`, dispatch `ConfigAction` reboot, and then reset displayed content.

pNFS flow checks filesystem support in `FSObject.get_layout`/`commit_layout`, then delegates to layout subclasses. `LayoutFSObj` expands block extents and commits block layout updates. `FSLayoutFSObj` packs `nfsv4_1_file_layout4` using DS filehandles and uses `FileLayoutFile` to stripe reads/writes/truncates through `DataServer` wrappers.

## State And Persistence Behavior
`StubFS_Mem` and `RootFS` are process-memory filesystems. `StubFS_Disk` persists metadata as pickled `m_<id>` files, file/directory data as `d_<id>` files, and filesystem metadata in a shelve DB named `fs_info`. `FSObject._last_sync` tracks whether the current change counter has reached disk. `UNSTABLE4` sync returns without writing and `FILE_SYNC4` updates `_last_sync`.

Per-object state includes metadata, in-memory file handles (`StringIO` or layout wrappers), directory entries, a small directory-cookie cache, `FileState`, locks, current layout tuple, mount overlay pointers, and config dirty flags. Block layout state is partly global in `test_layout_dict`; file-layout backing data is persisted on remote data servers through `dataserver.py`.

## Dependencies And Integration Points
The module depends on `nfs4state.FileState`, generated NFS constants/types/packers, `nfs4lib`, `locking.Lock/RWLock`, `config.ServerPerClientConfig`, `ConfigAction`, Python filesystem modules, pNFS block generated types, and a local `block` module. It integrates with server operation handlers for LOOKUP, CREATE, READ, WRITE, SETATTR, READDIR, layouts, device IDs, config pseudo-files, and pNFS DS access.

## Risks And Edge Cases
- The file mixes Python 2 and Python 3 assumptions: `cStringIO`, text `StringIO`, `chr(0)` writes, pickle opened in text mode, division producing floats, and string/bytes mismatches can all break binary NFS data paths.
- `FSObject.isempty` assumes `entries` exists, which is not true for all object types.
- `unlink` decrements refcount and syncs the target but does not call `destroy` or deallocate IDs when refcount reaches zero.
- Directory verifier cache is timestamp keyed, small, and per-object; concurrent clients can see `NFS4ERR_NOT_SAME`.
- `ConfigObj._build_entries` encodes object identity into bit fields and comments admit unused bits are not carefully checked.
- `StubFS_Disk` opens pickle/data files in text mode and can corrupt bytes data.
- pNFS block layout code mutates global test layout state and has many explicit stubs around alignment, allocation locking, commit semantics, and poisoned reads.
- File layout striping assumes active DS count is nonzero and every DS has a cached filehandle.

## Test Signals
Signals include correct NFS attribute masks and partial-set errors, file size/read/write/truncate behavior, directory lookup/readdir cookies, mount traversal, config pseudo-file read/write/reboot/error-injection behavior, disk-backed restart preservation, read-only root errors, block layout GET/COMMIT behavior, file-layout DS open/close/read/write/truncate integration, and lock-safe concurrent access to object data.
