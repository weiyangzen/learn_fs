# File Research: sources/os/linux/linux/fs/ocfs2/ioctl.c

`ioctl.c` implements OCFS2’s file attribute operations and user ioctl dispatch. It handles allocation-space ioctls, volume resize/group changes, reflink, aggregated filesystem info requests, trim, and move-extents dispatch.

Main responsibilities:
- Implements `ocfs2_fileattr_get()` and `ocfs2_fileattr_set()` for generic fileattr integration. Attribute set takes the inode metadata lock, preserves non-modifiable bits, enforces immutable/append capability checks under OCFS2 locking, starts an inode-update transaction, updates ctime, and writes the dinode.
- Defines helpers for `OCFS2_IOC_INFO`, including request flag management, coherent/non-coherent mode handling, and safe copy to/from user.
- Provides individual info request handlers for block size, cluster size, max slots, label, UUID, feature flags, journal size, free inode counts, and free-fragmentation statistics.
- Free inode reporting scans per-slot inode allocator system files. In coherent mode it uses system inode lookup and cluster locks; in non-coherent mode it resolves raw system inode block numbers and reads blocks directly.
- Free fragmentation reporting scans global bitmap chain records and group descriptors, builds a power-of-two chunk histogram, and reports min/max/average free extents plus free cluster totals. Non-coherent raw reads include extra validation of group bitmap size.
- Validates info request magic, code, and structure size before dispatching; unknown request codes are returned unfilled for forward/backward compatibility.
- Handles compat pointer arrays for 32-bit userspace when `CONFIG_COMPAT` is enabled.
- Dispatches `ocfs2_ioctl()`:
  - `OCFS2_IOC_RESVSP*` and `OCFS2_IOC_UNRESVSP*` to `ocfs2_change_file_space()`.
  - `OCFS2_IOC_GROUP_EXTEND` and group add ioctls with `CAP_SYS_RESOURCE` and mount-write protection.
  - `OCFS2_IOC_REFLINK` to `ocfs2_reflink_ioctl()`.
  - `OCFS2_IOC_INFO` to the info aggregator.
  - `FITRIM` with `CAP_SYS_ADMIN`, discard support checks, and `ocfs2_trim_fs()`.
  - `OCFS2_IOC_MOVE_EXT` to `ocfs2_ioctl_move_extents()`.
- Implements `ocfs2_compat_ioctl()` for compat reflink/info pointer translation and forwards supported commands to the native ioctl path.

Key interactions:
- Uses inode/journal helpers for attribute persistence.
- Uses system-file lookup and raw block reads for coherent vs non-coherent info modes.
- Exposes `move_extents.c` through the ioctl surface.
- Relies on user ABI structures from OCFS2 filesystem headers.

Key invariants:
- Mutating ioctls acquire mount write access where needed.
- Privileged resize/trim operations require capabilities.
- Info aggregation processes small typed request structures to preserve ABI compatibility.
