# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_mirror.c

## Purpose
Implements mirror-like vdev operations for `mirror`, `replacing`, and `spare` vdevs. It opens/closes children, selects read children based on availability, DTL freshness, load, and locality, fans writes out to all children, retries reads, and repairs stale or damaged replicas.

## Main Structures
- `mirror_child_t` tracks child vdev, offset, last error, calculated load, whether tried/skipped, and whether an error was speculative.
- `mirror_map_t` owns per-I/O child records plus an array of preferred child indexes, and flags for root DVA reads and replacing/spare resilvering.
- Mirror kstats count load-selection outcomes for rotating/non-rotating devices and preferred-child selection.

## Key Functions
- `vdev_mirror_load()` computes a load score from vdev queue depth and last issued offset. It applies different sequential/seek penalties for rotating and non-rotating media; root DVA selection treats all copies equally.
- `vdev_mirror_map_init()` builds a map either from a block pointer's DVAs for root/ditto reads (`io_vd == NULL`) or from the mirror/replacing/spare children. Sequential scrub reads can limit initial work to one sorted DVA until retry.
- `vdev_mirror_open()` opens all children, computes the mirror size as the minimum child size and max ashift, and fails only if all children fail.
- `vdev_mirror_child_select()` skips unreadable children and DTL-missing children, gathers lowest-load candidates, randomizes among ties, and falls back to untried stale children only when no clean choice exists.
- `vdev_mirror_io_start()` sends scrub reads with checksummable data to every child unless the replacing vdev is resilvering; normal reads go to one selected child; writes go to all children.
- `vdev_mirror_io_done()` accepts partial writes if at least one copy succeeded for normal mirrors, retries reads on additional children when no good copy exists, sets worst error when exhausted, and issues repair writes when a good copy exists and repair is warranted.
- `vdev_mirror_state_change()` sets parent state to offline/no replicas, degraded, or healthy based on child fault/degraded counts.
- `vdev_mirror_dumpio()` performs dump I/O on children, stopping after the first successful read but attempting all children for writes.

## Important Behavior And Invariants
- Replacing/spare vdevs suppress scrub reads to resilvering children because the new device may not yet contain the block.
- A mirror read can repair children not tried when scrub/resilver/indirect-vdev/DTL conditions imply they may be stale.
- Partial writes are intentionally treated as success in some cases, with comments noting future write reallocation policy could be stricter.
- For untrusted pool configs, invalid DVAs are filtered before root mirror map creation; if none remain, the parent zio is failed with `ENXIO`.

## Registered Ops
`vdev_mirror_ops`, `vdev_replacing_ops`, and `vdev_spare_ops` share open/close/asize/io/state/dump handlers, differ only by type string.
