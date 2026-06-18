# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_label.c

## Purpose
Implements ZFS vdev label handling: label layout addressing, config nvlist generation, label reads/writes, device-in-use checks, initial label creation, boot environment label storage, uberblock loading/syncing, and transactionally consistent config sync.

## Label Model
Each leaf has four labels: two at the beginning and two at the end of the device. Each label contains padding, a packed `vdev_phys_t` nvlist, a boot-environment pad area, and an uberblock ring. Config updates write one label set before the uberblock and the other after it so power loss can be resolved using label and uberblock txgs.

## Main Responsibilities
- Compute physical label offsets and reverse-map offsets to label numbers.
- Generate vdev config nvlists, including identity, topology, metaslab fields, DTL objects, indirect-vdev metadata, ZAP object ids, state flags, aux state, stats, and child arrays.
- Read the best label config from a vdev subject to a maximum txg.
- Detect whether candidate devices are already in active use, spare use, or L2ARC use.
- Initialize labels for new pool devices, replacements, spares, L2ARC devices, removals, and splits.
- Read/write the boot environment area from/to all readable/writable leaf labels.
- Load the best uberblock across the whole vdev tree and read the associated config.
- Sync labels and uberblocks in a crash-consistent sequence.

## Key Functions
- `vdev_label_offset()` maps label number plus offset inside `vdev_label_t` to device offset, placing labels 0/1 at start and 2/3 at end.
- `vdev_config_generate_stats()` packs standard and extended vdev stats including queue active/pending counts, latency histograms, I/O size histograms, and slow I/O count.
- `vdev_config_generate()` recursively builds a vdev nvlist. It handles top-level fields, indirect mapping/birth objects, MOS-only ZAP fields, deferred resilver marker, removable-device indirect-size estimates, leaf state flags, and nested children.
- `vdev_top_config_generate()` records root child count and hole array for top-level namespace holes.
- `vdev_label_read_config()` reads all labels, unpacks nvlists, and selects the newest label whose txg does not exceed the requested txg; if no config is found, retries with `ZIO_FLAG_TRYHARD`.
- `vdev_inuse()` reads labels and checks pool/device GUIDs, pool state, txg/create-txg, spare registry, L2ARC registry, and read-only imported pools.
- `vdev_label_init()` recurses through children, rejects dead/in-use leaves, adjusts GUIDs for shared spares/L2ARC, creates the initial txg-0 config label or special spare/L2ARC label, zeros the bootenv pad, writes an uberblock template with txg 0, and writes all four labels.
- `vdev_label_read_bootenv()` gathers the first checksum-valid bootenv block from all leaves and interprets raw GRUB env data, nvlist data, empty nvlist data, or FreeBSD bootonce strings.
- `vdev_label_write_bootenv()` validates packed size, recursively writes leaves, encodes raw or nvlist bootenv payloads, and succeeds if any disk writes all labels successfully.
- `vdev_uberblock_load()` scans all uberblock rings on all readable leaves, picks the best uberblock by txg, timestamp, then MMP sequence, and reads a matching label config from the same vdev.
- `vdev_uberblock_sync_list()` writes uberblocks to all supplied vdev trees, flushes write caches, and requires at least one successful write to a known-visible vdev.
- `vdev_label_sync_list()` writes even or odd labels for all dirty vdevs, tracks at least one good write per normal top-level vdev, ignores errors for log/cache/aux devices, and flushes.
- `vdev_config_sync()` is the high-level sync order: flush txg data, write even labels, write uberblocks, update MMP data if enabled, then write odd labels, retrying once with `TRYHARD` on failures.

## Important Behavior And Invariants
- Label selection must not use a config newer than the selected uberblock unless extreme rewind explicitly retries without txg restrictions.
- New devices are pre-labeled with txg 0 so failed creates do not leave active-looking pool labels.
- Config nvlists can fail to pack if too large; initialization maps `EFAULT` from `nvlist_pack()` to `ENAMETOOLONG`.
- `vdev_config_sync()` is designed to be idempotent after partial failure.
- Multihost MMP reserves some uberblock slots from normal txg cycling.

## Dependencies
Uses nvlist/fnvlist APIs, ZIO physical I/O, ABD buffers, SPA config and dirty lists, uberblock comparison/update, MMP helpers, vdev stats, DTL/space maps, scan/removal/checkpoint stats, ZAP metadata, and bootenv constants.
