# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/fsctl.c

## Scope
Implements Ext2 filesystem-control dispatch for volume mount, verify, lock/unlock, dismount, invalidate, retrieval-pointer queries, oplocks, volume dirty state, extended DASD access, Windows reparse-point operations backed by ext2 symlinks, and cache purge/teardown paths.

## Key Elements
- `Ext2FileSystemControl()` dispatches `IRP_MN_USER_FS_REQUEST`, `IRP_MN_MOUNT_VOLUME`, and `IRP_MN_VERIFY_VOLUME`.
- `Ext2UserFsRequest()` maps user FSCTLs to handlers for reparse points, volume lock/unlock/dismount/mounted checks, invalidate volumes, oplocks, dirty-state query, and retrieval-pointer APIs.
- `Ext2LockVcb()`, `Ext2LockVolume()`, `Ext2UnlockVcb()`, and `Ext2UnlockVolume()` enforce open-handle checks, set/clear `VCB_VOLUME_LOCKED`, and update `VPB_LOCKED`.
- `Ext2MountVolume()` creates the per-volume device object, reads and validates the ext2 superblock magic, initializes the VCB, handles old VPB/VCB matching, marks the VPB mounted, inserts the VCB globally, and dereferences the target device on success.
- `Ext2VerifyVcb()` and `Ext2VerifyVolume()` perform removable-media verification, change-count checks, superblock UUID/name comparison, write-protection refresh, and purge/dismount-pending handling on wrong media.
- `Ext2DismountVolume()` flushes files/volume, purges cache, and calls `Ext2CheckDismount()` to detach or replace VPBs.
- `Ext2CheckDismount()` coordinates global and VCB resources plus the VPB spin lock to remove the VCB from global lists, mark dismount pending, allocate a replacement VPB for forced dismount, tear streams down, and destroy VCBs when references are gone.
- `Ext2PurgeVolume()` and `Ext2PurgeFile()` flush or purge cache-manager sections, image sections, group descriptor buffer heads, and per-FCB section objects.
- Retrieval-pointer support uses `Ext2BuildExtents()` to fill `RETRIEVAL_POINTERS_BUFFER` or internal paging-file mapping arrays.
- Reparse-point support treats ext2 symlinks as Windows `IO_REPARSE_TAG_SYMLINK`, translating slash direction and OEM/Unicode names.

## Dependencies
Depends on Ext2 VCB/FCB/CCB/MCB structures, `Ext2BuildExtents()`, inode read/write/truncate helpers, VCB initialization/destruction, cache-manager APIs, FsRtl oplock/file-lock APIs, VPB spin-lock operations, lower disk IOCTL helpers, NLS conversion helpers, and global VCB list state.

## Behavior/Risks
- The mount path assumes successful `Ext2LoadSuper()` plus `EXT2_SUPER_MAGIC` is enough to claim the volume before `Ext2InitializeVcb()` performs deeper setup.
- Reparse handling only supports relative symlink reparse buffers and explicitly rejects other tags or absolute symlink flags.
- `Ext2QueryRetrievalPointers()` contains `DbgBreak()` calls, so this path appears diagnostic or unfinished.
- `Ext2GetRetrievalPointers()` uses `BLOCK_BITS` conversions and must keep VCN/LCN units consistent with Windows callers.
- Dismount and forced VPB replacement are highly stateful; correctness depends on VPB reference counts, `VCB_NEW_VPB`, `VCB_DISMOUNT_PENDING`, and global VCB resource ordering.
- Purge paths deliberately acquire paging resources before cache flush/purge to synchronize with mapped and cached IO.
