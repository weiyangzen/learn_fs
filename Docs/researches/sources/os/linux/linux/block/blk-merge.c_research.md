# File Research: sources/os/linux/linux/block/blk-merge.c

## Summary
Implements bio splitting to queue limits and bio/request merge logic for the block layer, including segment accounting, gap checks, discard merging, scheduler merging, rq-qos merge charging, integrity, crypto, cgroup, zoned, and atomic-write constraints.

## Main Responsibilities
- Determine where bios must split to satisfy queue limits.
- Split discard, read/write, zone append, and write-zeroes bios.
- Recalculate request physical segment counts.
- Check back, front, and discard merge eligibility.
- Merge bios into requests and requests into adjacent requests.
- Preserve accounting, tracing, crypto, integrity, and mixed failfast state.

## Key APIs
- `bio_submit_split_bioset()`.
- `bio_split_discard()`.
- `bio_split_io_at()`.
- `bio_split_rw()`.
- `bio_split_zone_append()`.
- `bio_split_write_zeroes()`.
- `bio_split_to_limits()`.
- `blk_recalc_rq_segments()`.
- `ll_back_merge_fn()`.
- `blk_attempt_req_merge()`.
- `blk_rq_merge_ok()`.
- `blk_try_merge()`.
- `bio_attempt_back_merge()`.
- `blk_attempt_plug_merge()`.
- `blk_bio_list_merge()`.
- `blk_mq_sched_try_merge()`.

## Important Behavior
Splitting checks DMA alignment, crypto data unit alignment, segment count, maximum bytes, maximum sectors, physical/logical block alignment, virtual boundary gaps, atomic-write restrictions, and `REQ_NOWAIT`. If a split is required for polled I/O, polling is cleared to avoid direct-I/O iopoll hangs.

Merge checks reject incompatible operations, cgroups, integrity metadata, crypto contexts, write hints, write streams, I/O priorities, atomic-write flags, queue boundary limits, segment limits, and gap constraints. Zoned write plugging blocks front merges to sequential zones.

Mixed failfast merges propagate per-request failfast flags down into each bio and mark `RQF_MIXED_MERGE`, because the merged request can no longer represent one uniform failfast setting.

## State and Synchronization
Request merge operations update bio chains, `biotail`, `__sector`, `__data_len`, physical and integrity segment counts, `phys_gap_bit`, accounting counters, crypto keyslots, and scheduler/elevator state. Plug merging deliberately avoids elevator callbacks because plugged requests are not yet on the scheduler.

## Risks
This is a central correctness boundary: accepting a bad merge can violate driver DMA limits or semantic constraints, while rejecting too much hurts performance. Atomic writes and zone append/write-plugged writes are especially sensitive because splitting or reordering can break their semantics.
