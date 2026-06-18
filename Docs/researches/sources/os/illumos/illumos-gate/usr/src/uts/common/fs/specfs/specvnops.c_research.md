# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/specfs/specvnops.c

Special-device vnode operations for illumos `specfs`, mediating character/block device access through snodes, common snodes, real backing vnodes, STREAMS state, device-policy checks, and VM/page-cache interfaces.

Key responsibilities:
- Defines `spec_vnodeops_template` for special-file VOPs: open, close, read, write, ioctl, getattr/setattr/access/create, fsync, inactive, fid, seek, locks, realvp, getpage/putpage, map/addmap/delmap, poll, dump, pageio, ACL, and pathconf.
- Maintains common-snode open/reference serialization using `spec_lockcsp()`, `SN_HOLD`, `SN_RELE`, `SLOCKED`, `SWANT`, and `SCLOSING`.
- Computes and caches device size in `spec_size()`, using driver properties such as `Size`, `size`, `Nblocks`, `nblocks`, `blksize`, and `device-blksize`, with `UNKNOWN_SIZE` for unavailable block-device sizes.
- Handles device opens in `spec_open()`, including devinfo association, `VFS_NODEVICES`, fencing, policy checks, STREAMS vs non-STREAMS dispatch, clone opens, open/close exclusion, device contracts, offset-capability flags, and EINTR behavior for drivers that opt in.
- Handles last-close semantics in `spec_close()`, including file lock/share cleanup, size invalidation, clone devinfo reassociation, and actual `device_close()` only when common-snode open/mapping references reach zero.
- Implements character and block device I/O: STREAMS read/write via `strread`/`strwrite`, character devices via `cdev_read`/`cdev_write`, and block devices via segmap/VPM data copy against the common vnode.
- Implements block-device VM operations: `spec_getpage()`, `spec_getapage()`, `spec_putpage()`, `spec_putapage()`, and `spec_startio()` use page clustering, read-ahead, page zeroing past device size, `pageio_setup()`, and `bdev_strategy()`.
- Implements device mmap support through `spec_map()`, `spec_char_map()`, and `spec_segmap()`, choosing old `mmap`, `devmap_setup`, driver `segmap`, or `segvn` mappings for block devices.
- Forwards attributes, ACLs, pathconf, fid, access, and setattr operations to `s_realvp` where available; otherwise fabricates special-file metadata from the snode.

Dependencies:
- Uses kernel device switch and DDI interfaces: `dev_open`, `device_close`, `cdev_*`, `bdev_*`, `devopsp`, `devnamesp`, `e_ddi_hold_devi_by_dev`, and `spec_assoc_vp_with_devi`.
- Uses STREAMS internals: `stropen`, `strread`, `strwrite`, `strioctl`, `strpoll`, `strctty`, stream head fields, and clone/qassociate handling.
- Uses VM/page infrastructure: `segmap`, `vpm`, `segvn`, `segdev`, `page_*`, `pvn_*`, `pageio_*`, `hat`, and vnode page-cache helpers.
- Depends on snode state from `sys/fs/snode.h` and global specfs state such as `stable_lock`, `snode_cache`, `spec_vfs`, and device fencing flags.

Concurrency and locking:
- Common-snode serialization is central; open, close, addmap, and delmap coordinate through `spec_lockcsp()` and `s_lock`.
- `spec_inactive()` removes snodes under `stable_lock`, drops vnode references carefully, updates real vnode times, releases devinfo/device-policy holds, and frees the snode.
- Mapping count `s_mapcnt` participates in close decisions; final `delmap` may close the device if open count is zero.

Notable risks:
- Open/close and clone handling is highly stateful; incorrect `s_count`, `s_mapcnt`, `SNEEDCLOSE`, or `SDIPSET` transitions can leak device references or close active devices.
- Size caching deliberately avoids calling driver property callbacks before attach/open to avoid driver panics; changing this can expose latent driver bugs.
- Block-device I/O depends on correct EOF/device-size clipping and page zeroing; errors here can expose stale memory or corrupt cached pages.
- Fencing policy is asymmetric by design: configuration/detection paths fail, but unconfiguration and some I/O paths are allowed through.
