# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs_fm.c

Implements ZFS Fault Management Architecture event generation for pool, vdev, block, data, device, delay, and checksum errors, plus resource events such as removal, autoreplace, and state changes. Kernel-only sections build and post FMA nvlists; non-kernel builds retain validity wrappers and shared interfaces.

`zfs_ereport_start()` constructs the common ereport and detector payload. It validates whether the event should be emitted, serializes ENA generation under `spa_errlist_lock`, chooses a pool-wide ENA during load or a logical-ZIO ENA for related I/O failures, sets the FMA class, detector FMRI, pool metadata, failmode, vdev metadata, parent vdev metadata, ZIO error/offset/size, previous vdev state, and logical bookmark fields.

`zfs_ereport_is_valid()` suppresses misleading or redundant events: try-import and recovery loads, repeated failed opens, non-read/write ZIO failures, inaccessible vdevs already failing due to probes/removal, checksum reads from missing DTL regions, probe failures after removal, and bogus delay events from unqueued I/O.

Checksum reporting has a staged path. `zfs_ereport_start_checksum()` captures vdev-specific checksum report context and links a report onto the logical ZIO. `zfs_ereport_finish_checksum()` annotates and posts the saved report when good/bad data are available. `zfs_ereport_post_checksum()` is the immediate one-shot version. `zfs_ereport_send_interim_checksum()` posts a partial report, and `zfs_ereport_free_checksum()` frees report state.

`annotate_ecksum()` compares good and bad ABD buffers to enrich checksum ereports. It records expected/actual checksums and algorithm when supplied, tracks byte ranges that differ, compresses many ranges by increasing the minimum gap via `shrink_ranges()`, stores inline set/cleared bit arrays for small corruptions, or stores per-bit histograms for larger corruptions. It can drop an event when good and bad buffers are identical and the caller requested that behavior.

`zfs_ereport_post()` posts ordinary ereports and frees the associated nvlists. `zfs_post_common()` and wrappers `zfs_post_remove()`, `zfs_post_autoreplace()`, and `zfs_post_state_change()` emit resource events used by diagnosis/retire agents to interpret vdev removal, autoreplace behavior, and state recovery.

The file’s core design goal is correlation: events for one logical I/O share an ENA even if failures happen through mirrors, RAID-Z, gang blocks, retries, or delegated I/O, while purely physical/cache/aggregation noise is suppressed or isolated.
