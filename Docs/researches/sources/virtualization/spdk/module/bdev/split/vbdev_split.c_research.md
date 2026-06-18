# File Research: sources/virtualization/spdk/module/bdev/split/vbdev_split.c

## Purpose
Implements a simple virtual bdev module that slices one base bdev into multiple fixed-size `spdk_bdev_part` child bdevs.

## State
`struct spdk_vbdev_split_config` stores base bdev name, split count, optional split size in MiB, tailq of parts, and part-base pointer. `g_split_config` stores all active or pending split configs.

Per-I/O context stores the channel and bdev I/O for retry through `spdk_bdev_queue_io_wait()`.

## Lifecycle
`create_vbdev_split()` adds config and attempts immediate construction. If the base bdev does not exist, the config remains pending and `vbdev_split_examine()` creates the splits when the base appears.

`vbdev_split_create()` constructs a `spdk_bdev_part_base`, computes split size, clamps split count to the maximum possible, and registers child parts named `<base_bdev>p<index>`. `vbdev_split_destruct()` hot-removes all split parts and deletes the config.

## I/O Path
The module delegates I/O to `spdk_bdev_part_submit_request()`. Reads acquire an aligned buffer first; all other supported part operations pass through directly. `-ENOMEM` submission failures are queued for retry on the base channel.

## JSON
The module-level config writer emits `bdev_split_create` records containing base bdev, split count, and split size.

## Invariants And Risks
- Duplicate split configs for a base bdev are rejected.
- Split count must be nonzero.
- Split size must be aligned to the base bdev block size.
- If construction fails after part-base creation, the code hot-removes/free the part base to unwind.
