# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbclnt/smbfs/smbfs_vfsops.c

## Purpose
SMBFS VFS/module operations: module load/unload, VFS op registration, mount setup, unmount teardown, root lookup, filesystem statistics, sync, and VFS resource cleanup.

## Mount Options and Globals
- `smbfs_default_opt_acl`
  - Controls whether `-o acl` is enabled by default; default is off.
- `smbfs_tq_nthread`
  - Per-mount taskq thread count; default one thread.
- Mount options include:
  - `intr` / `nointr`
  - `acl` / `noacl`
  - `xattr` / `noxattr`
  - fake-kernel-only `noac`
- `smbfs_mountcount`
  - Prevents module unload while mounts or forced-unmount remnants exist.

## Key Functions
- `_init()`
  - Verifies `nsmb` ABI version.
  - Initializes subr, VFS, and client layers.
  - Installs the filesystem module or fake-kernel filesystem.
- `_fini()`
  - Refuses unload while `smbfs_mountcount` is nonzero.
  - Removes module/fake filesystem and tears down SMBFS layers and vnode/VFS ops.
- `smbfsinit(...)`
  - Registers VFS ops and vnode ops.
- `smbfs_mount(...)`
  - Validates mount permissions and mountpoint type.
  - Copies in and validates `smbfs_args`.
  - Rejects remount.
  - Gets `smb_share_t` from the netsmb device fd.
  - Enforces zone and Trusted Extensions label policy in kernel builds.
  - Allocates and initializes `smbmntinfo_t`.
  - Sets attribute cache timers, mount uid/gid/modes, ACL/intr/noac flags.
  - Queries remote filesystem attributes/capabilities.
  - Forces `noxattr` when named streams are unsupported.
  - Forces `noacl` when persistent ACLs are unsupported.
  - Allocates a unique device id/fsid.
  - Registers VFS features `VFSFT_XVATTR` and `VFSFT_SYSATTR_VIEWS`.
  - Creates and holds the root smbnode at remote path `\`.
  - Creates the per-mount taskq for async work such as putpage/delmap.
- `smbfs_unmount(...)`
  - Checks unmount permission.
  - For non-forced unmount, flushes dirty nodes and rejects busy node tables/root refs.
  - Marks `VFS_UNMOUNTED`.
  - Releases the mount-held root vnode.
  - Destroys inactive node-table entries.
  - Kills the SMB share and destroys the per-mount taskq.
  - Deletes mount kstats.
- `smbfs_root(...)`
  - Returns a hold on the root vnode if called from the owning zone and mount is alive.
- `smbfs_statvfs(...)`
  - Serializes remote statfs refresh through `smi_lock` and `smi_statvfs_cv`.
  - Uses cached stats until `smi_statfstime`.
  - Fills local statvfs fields not supplied over the wire.
- `smbfs_sync(...)`
  - Ignores `SYNC_ATTR`.
  - Flushes all SMBFS mounts in zone when `vfsp == NULL`, otherwise flushes one mount.
- `smbfs_freevfs(...)`
  - Removes mount from zone list, frees `smbmntinfo_t`, and decrements mount count.
- `smbfs_mount_label_policy(...)`
  - Kernel-only Trusted Extensions MAC policy.
  - Allows read-write, read-only read-down, or denies based on zone/server labels.

## Important Interactions
- Uses `smb_dev2share`, `smb_share_rele`, and `smb_share_kill` from netsmb.
- Uses node-cache helpers from `smbfs_subr2.c`.
- VFS unmount deliberately keeps the share alive until after node cleanup.
