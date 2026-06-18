# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/mntfs/mntvnops.c

## Role

Implements vnode operations and snapshot machinery for mntfs. This is the main implementation of reading `/etc/mnttab` and servicing mount-table ioctls.

## Major Responsibilities

- Generates textual `/etc/mnttab` entries from in-kernel `vfs_t` state.
- Provides per-open stable snapshots for `read(2)` and mnttab ioctls.
- Maintains a zone-local database of mount entries with birth/death times and refcounts.
- Supports public and private `mntio` ioctls used by mnttab consumers.
- Implements vnode open/close/read/getattr/access/seek/poll/cmp behavior.

## Snapshot Design

The large block comment describes the core model:

- Each zone has a mount database at `zone_mntfs_db`, protected by `zone_mntfs_db_lock`.
- Each database element (`mntelem_t`) stores one rendered mount-table line plus an `extmnttab` offset table.
- Elements have birth/death times so a snapshot can see the database as it existed at snapshot creation.
- A snapshot (`mntsnap_t`) holds references to all matching elements.
- Elements are freed only when no active snapshot references them.
- Each open mntfs vnode has separate snapshots for read and ioctl use, because `getmntent(3C)` and `read(2)` have independent stream positions on the same fd.

## Key Functions

- `mntfs_devsize()` / `mntfs_devprint()`: Size and print legacy `dev=xxx` option.
- `mntfs_newest()`: Compares two `timespec_t` values.
- `mntfs_optsize()` / `mntfs_optprint()`: Size and print visible mount options, zone option, and legacy device option.
- `mntfs_populate_text()`: Builds the tab-delimited textual mount entry and fills `struct extmnttab` offsets/major/minor/hidden metadata.
- `mntfs_text_len()`: Computes required text size for one VFS entry.
- `mntfs_destroy_elem()`: Frees an element.
- `mntfs_elem_in_range()`: Tests whether an element belongs to a snapshot.
- `mntfs_get_next_elem()`: Iterates visible elements for a snapshot.
- `mntfs_freesnap()`: Releases snapshot holds and removes unreferenced elements.
- `mntfs_snapshot()`: Synchronizes the zone database with current kernel VFS list and initializes a snapshot.
- `mntfs_getmntopts()`: Public helper to stringify a VFS mount option set.
- `mntopen()`: Rejects write opens and creates a fresh per-open mntnode/vnode.
- `mntclose()`: On final close, frees read/ioctl snapshots and decrements open count.
- `mntread()`: Reads a stable snapshot into user space with per-snapshot offset caching.
- `mntgetattr()`: Computes attributes for `/etc/mnttab`, including consistent size/mtime.
- `mntaccess()`: Rejects write/exec and delegates read checks to the underlying mountpoint vnode.
- `mntgetnode()` / `mntfreenode()`: Allocate/free per-open synthetic vnode state.
- `mntseek()`: Marks ioctl snapshot rewind when lseek rewinds to offset 0.
- `mntpoll()`: Reports readable status and supports `POLLRDBAND` notification on mnttab changes.
- `mntfs_same_word()`: Compares user preference fields against tab-delimited entry fields.
- `mntfs_special_info_string()` / `mntfs_special_info_element()`: Resolve special device resource paths to type/major/minor for robust matching.
- `mntfs_import_addr()`: Converts user pointers inside an imported user buffer to kernel-buffer pointers.
- `mntfs_copyout_elem()`: Copies an entry and its pointer fields to userland for mnttab ioctls.
- `mntioctl()`: Implements mntfs ioctl command set.
- `mntcmp()`: Treats two per-open vnodes as the same mnttab instance when they share the same VFS.

## Ioctl Support

`mntioctl()` supports:

- `MNTIOC_NMNTS`: Return number of mounted resources in the ioctl snapshot.
- `MNTIOC_GETDEVLIST`: Return major/minor pairs for snapshot entries.
- `MNTIOC_SETTAG` / `MNTIOC_CLRTAG`: Set or clear mount tags after zone-aware path translation.
- `MNTIOC_SHOWHIDDEN`: Enable hidden mount entries for this open vnode.
- `MNTIOC_GETMNTANY`: Find next entry matching user-provided preferences, including special-device major/minor matching.
- `MNTIOC_GETMNTENT` / `MNTIOC_GETEXTMNTENT`: Return next mount entry.

It also handles 32-bit data model structure layouts under `_SYSCALL32_IMPL`.

## Database Update Semantics

`mntfs_snapshot()` walks the relevant VFS list:

- Global zone uses the global circular VFS list.
- Non-global zones use `zone_vfslist`.
- If a non-global zone lacks an explicit root VFS entry, a dummy VFS entry is cloned from the zone root vnode’s VFS.
- Existing elements are matched by high-resolution VFS creation time.
- Stale elements are killed by setting death time.
- Remounted or changed VFS entries cause old elements to die and new elements to be inserted.
- Hidden entries are included only if `MNT_SHOWHIDDEN` is active.

## Edge Cases and Semantics

- Read snapshots are refreshed on first read or when read offset is zero.
- Ioctl snapshots are refreshed on first ioctl use or after rewind marker.
- `mntgetattr()` goes to extra effort to keep reported size and mtime consistent around mount-table changes.
- `mntfs_enabledev` preserves the historical `dev=xxx` option.
- Zone path visibility and translation are applied to resource and mountpoint fields.
- The synthetic file is read-only and non-executable.
- `mntpoll()` uses the newer of read/ioctl snapshot mtimes.
- `MNTIOC_GETMNTANY` may temporarily drop the database lock to inspect special-device type through filesystem lookup.

## Dependencies

Depends on VFS list locking, zone mount databases, mount option structures, vnode lookup/getattr, copyin/copyout, poll hooks, DTrace probes, mntfs private structures, and public/private mnttab ioctl ABI definitions.
