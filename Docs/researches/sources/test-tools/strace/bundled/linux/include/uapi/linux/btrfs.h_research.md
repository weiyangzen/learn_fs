<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/btrfs.h -->
# sources/test-tools/strace/bundled/linux/include/uapi/linux/btrfs.h

Purpose: large Btrfs filesystem ioctl UAPI header defining user-visible structures, flags, feature bits, and ioctl numbers for subvolumes, devices, scrub, balance, search, cloning, quota, send/receive, encoded I/O, and shutdown.

Important APIs/types: key structs include `btrfs_ioctl_vol_args`, `btrfs_qgroup_limit`, `btrfs_qgroup_inherit`, `btrfs_ioctl_vol_args_v2`, `btrfs_scrub_progress`, `btrfs_ioctl_scrub_args`, device replace params/status/args, device info, fs info, feature flags, packed `btrfs_balance_args`, balance progress/args, inode lookup structs, tree search key/header/search args v1/v2, clone/defrag/same extent/space/data container/logical inode/dev stats/quota/send/subvolume/encoded I/O/subvolume wait structures. Ioctl macros define `BTRFS_IOC_*` commands with magic `0x94` plus `BTRFS_IOC_SHUTDOWN` using XFS-compatible magic.

Control flow: declarative ABI with unions, flexible arrays, pointer fields, packed structs, and flag masks documenting valid combinations.

State and persistence: real ioctls can mutate filesystem metadata, devices, quotas, balances, scrub state, subvolumes, and encoded file data. The header itself has no runtime state.

Dependencies and integration: includes `<linux/types.h>`, `<linux/ioctl.h>`, and `<linux/fs.h>`. Strace uses it for deep Btrfs ioctl decoding.

Risks: this is a high-churn, high-blast-radius ABI surface. Pointer fields and flexible arrays require careful bounded decoding. Some ioctl numbers are intentionally shared by get/set/supported feature variants and encoded read/write, so direction/type must be inferred from macro usage. Struct padding/reserved fields must remain zero for forward compatibility. Test signals: ioctl decoder tests should cover representative v1/v2 structs, flexible array counts, feature flags, balance filters, send flags, encoded I/O compression values, and shared-number ioctl disambiguation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/bundled/linux/include/uapi/linux/btrfs.h -->
