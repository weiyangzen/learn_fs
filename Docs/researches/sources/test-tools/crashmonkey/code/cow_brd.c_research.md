# sources/test-tools/crashmonkey/code/cow_brd.c

## Purpose

`cow_brd.c` implements CrashMonkey's copy-on-write RAM block device kernel module. It is derived from Linux brd/ramdisk code and adds snapshot devices: base `cow_ramN` disks can be made read-only for snapshotting, while `cow_ram_snapshotS_N` devices read unchanged pages from their parent and store modified pages locally. This supports crash-consistency experiments where tests run against snapshots and can restore or wipe device state through ioctls.

## Important APIs, Types, and Functions

- Constants: `SECTOR_SHIFT`, `PAGE_SECTORS_SHIFT`, `PAGE_SECTORS`, `DEFAULT_COW_RD_SIZE`, and `DEVICE_NAME`.
- `struct brd_device` holds the device number, parent pointer, writable/snapshot flags, request queue, gendisk, list node, spinlock, and radix-tree page store.
- Page-store functions: `brd_lookup_page`, `brd_insert_page`, `brd_free_page`, `brd_zero_page`, and `brd_free_pages`.
- Data movement functions: `copy_to_brd_setup`, `discard_from_brd`, `copy_to_brd`, `copy_from_brd`, and `brd_do_bvec`.
- Request path: `brd_make_request` validates bounds/writability, handles discard, iterates bio segments, and completes or errors the bio using `bio_alias.h`.
- Optional XIP path: `brd_direct_access`.
- Control path: `brd_ioctl` handles `COW_BRD_SNAPSHOT`, `COW_BRD_UNSNAPSHOT`, `COW_BRD_RESTORE_SNAPSHOT`, and `COW_BRD_WIPE`.
- Module/device lifecycle: module params (`num_disks`, `num_snapshots`, `disk_size`, `max_part`), `brd_alloc`, `brd_free`, `brd_init_one`, `brd_del_one`, `brd_probe`, `brd_init`, and `brd_exit`.

## Control Flow

On module load, `brd_init` registers a block major, validates partition/minor limits, allocates `num_disks * (1 + num_snapshots)` devices, links snapshot devices to their parent base disk by `i % num_disks`, adds disks, registers the block region, and logs the number of disks and snapshots. `brd_alloc` creates the queue, installs `brd_make_request`, configures discard capabilities, allocates a gendisk, names it as base or snapshot, and sets capacity.

For I/O, `brd_make_request` obtains the target `brd_device` from the bio disk, rejects out-of-range requests, rejects writes/discards to non-writable base devices after snapshot activation, handles discard by zeroing pages, and otherwise iterates bio segments. `brd_do_bvec` inserts local pages before writes, maps pages with `kmap_atomic`, copies data into or out of the radix-tree store, and unmaps. Reads first consult the device's local pages, then the parent snapshot source, then return zeroes.

For snapshot control, ioctls on base devices toggle `is_writable` or wipe base pages. Ioctls on snapshot devices can restore the snapshot by freeing its local changed pages. Snapshot devices cannot be snapshotted/unsnapshotted/wiped as bases.

## State and Persistence Behavior

The device contents are volatile RAM pages stored in each device's `brd_pages` radix tree. Base devices persist data only until module unload or wipe. Snapshot devices persist only their changed pages; unchanged reads are served from the parent base disk. `COW_BRD_RESTORE_SNAPSHOT` discards a snapshot's local pages so it again reflects the parent. `COW_BRD_SNAPSHOT` makes the base read-only to preserve parent state while snapshots are active, and `COW_BRD_UNSNAPSHOT` makes it writable again.

## Dependencies and Integration Points

The module depends on Linux block-layer headers, radix trees, gendisk/request-queue APIs, module parameters, and version-specific bio aliases. It includes `disk_wrapper_ioctl.h` for ioctl constants and is built as `cow_brd.ko` by the Makefile through kbuild. User-space CrashMonkey tools and harness code interact with the exposed block devices and ioctls to create, restore, and wipe crash-test disks.

## Risks and Edge Cases

- Kernel API support is limited by `bio_alias.h` and in-file version conditionals.
- The discard path zeroes only full pages while `n >= PAGE_SIZE`; partial discards are ignored.
- `copy_to_brd` and `copy_from_brd` use pointer arithmetic on `void *`, which is a GNU C extension.
- `brd_mutex` is defined but unused; synchronization relies on spinlocks for radix-tree mutation and assumptions about open device lifetime.
- `brd_insert_page` copies parent data after insertion without locking the parent page against concurrent changes beyond the broader test assumptions.
- `COW_BRD_WIPE` assumes snapshots are not active, but the module does not enforce that beyond rejecting the ioctl on snapshot devices.
- In `brd_init`, some early validation failures return without unregistering a previously registered block major.
- Device major aliasing uses `MODULE_ALIAS_BLOCKDEV_MAJOR(RAMDISK_MAJOR)` while `register_blkdev` may allocate a dynamic major if `major_num` starts at 0.

## Test Signals

Build signals are successful kbuild compilation of `cow_brd.ko` for supported kernels. Runtime signals include module load creating expected `/dev/cow_ram*` and `/dev/cow_ram_snapshot*` devices, successful read/write round trips, snapshot reads falling back to parent pages, writes to snapshots not mutating parents, base writes rejected while snapshotted, restore clearing snapshot-local changes, wipe clearing base pages, discard returning zeroes, and clean module unload freeing pages without leaks or block-layer warnings.
