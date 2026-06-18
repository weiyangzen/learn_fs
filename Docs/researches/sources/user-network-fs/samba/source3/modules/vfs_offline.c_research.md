# sources/user-network-fs/samba/source3/modules/vfs_offline.c

## Purpose
`vfs_offline.c` marks every file in a share as offline/remote-storage capable for SMB clients. It is a small metadata filter that does not alter file I/O; it reports the filesystem capability `FILE_SUPPORTS_REMOTE_STORAGE` and sets `FILE_ATTRIBUTE_OFFLINE` in DOS attributes.

## Important APIs, Types, And Functions
- `offline_fs_capabilities()` ORs `FILE_SUPPORTS_REMOTE_STORAGE` into the next module's capability result.
- `offline_fget_dos_attributes()` ORs `FILE_ATTRIBUTE_OFFLINE` into `*dosmode` and then delegates to `SMB_VFS_NEXT_FGET_DOS_ATTRIBUTES`.
- `offline_fns` registers `.fs_capabilities_fn`, `.fget_dos_attributes_fn`, and not-implemented async DOS attribute hooks.
- `vfs_offline_init()` registers the module name `offline`.

## Control Flow
Each hook is a pass-through wrapper. Capabilities are delegated first through `SMB_VFS_NEXT_FS_CAPABILITIES` and augmented. File DOS attributes are modified in-place before calling the next VFS layer, so downstream layers can still add or validate attributes.

## State And Persistence
The module stores no per-handle or on-disk state. Its behavior is deterministic for every open file and every connection where the module is stacked.

## Dependencies And Integration Points
It depends on Samba's VFS operation chain and `FILE_SUPPORTS_REMOTE_STORAGE`/`FILE_ATTRIBUTE_OFFLINE` constants. It integrates with Windows Explorer and SMB clients that use offline file attributes or remote-storage capability bits.

## Risks
- Because all files are marked offline, clients may issue recall-oriented or remote-storage behavior even when the backend is ordinary local storage.
- Async DOS attribute hooks are explicitly unsupported through `vfs_not_implemented_*`; callers relying only on async path-based attributes may not see the offline bit.
- Attribute ordering in the VFS stack matters because this module mutates `dosmode` before delegating.

## Test Signals
- `fsctl`/capability queries should show remote storage support.
- DOS attribute queries on open files should include `FILE_ATTRIBUTE_OFFLINE`.
- Ordinary reads/writes should pass through unchanged.
- Async path DOS attribute calls should return the not-implemented path unless another stacked module supplies them.
