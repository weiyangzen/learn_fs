# File Research: sources/os/linux/linux/block/blk-integrity.c

## Summary
Implements block-layer data integrity metadata support for requests, including integrity scatterlist accounting, user metadata mapping, merge checks, metadata capability reporting, and sysfs attributes.

## Main Responsibilities
- Count integrity metadata scatterlist segments for a bio.
- Report logical block metadata capabilities through `FS_IOC_GETLBMD_CAP`.
- Map user-provided integrity metadata into a request.
- Decide whether integrity metadata allows request or bio merges.
- Expose integrity format and policy controls under the queue integrity sysfs group.

## Key APIs
- `blk_rq_count_integrity_sg()`.
- `blk_get_meta_cap()`.
- `blk_rq_integrity_map_user()`.
- `blk_integrity_merge_rq()`.
- `blk_integrity_merge_bio()`.
- `blk_integrity_profile_name()`.
- `blk_integrity_attr_group`.

## Important Behavior
Integrity merge checks require both sides either to have integrity metadata or not, matching `bip_flags`, matching application tag when `BIP_CHECK_APPTAG` is set, no integrity gap violation, and a segment count within `max_integrity_segments`.

`blk_get_meta_cap()` translates `struct blk_integrity` into userspace logical block metadata capability fields: integrity/ref-tag support, interval, metadata size, PI tuple size and offset, opaque metadata layout, checksum type, app tag size, and reference tag size.

Sysfs `read_verify` and `write_generate` are inverted relative to internal flags: writing true clears `BLK_INTEGRITY_NOVERIFY` or `BLK_INTEGRITY_NOGENERATE`. Updates are committed through frozen queue-limit updates.

## State and Synchronization
Integrity policy lives in `queue->limits.integrity`. Sysfs writes use `queue_limits_start_update()` and `queue_limits_commit_update_frozen()` to update limits safely.

## Risks
The sysfs boolean inversion is easy to misread. Merge correctness depends on all integrity fields staying aligned with the data request; incorrect segment counts or missed gap checks can create driver-visible metadata layout errors.
