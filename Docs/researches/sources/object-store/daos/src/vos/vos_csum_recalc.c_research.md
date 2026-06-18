# sources/object-store/daos/src/vos/vos_csum_recalc.c

## Purpose
`vos_csum_recalc.c` verifies input checksums and computes output checksums during VOS aggregation. Aggregation can coalesce several input physical segments into one logical output extent; this file validates the source data before writing the merged checksum metadata.

## Important APIs, Types, And Functions
- `calc_csum_params()` computes the checksum count and starting record index for an input segment, including prefix/suffix records needed by merge-window alignment.
- `csum_agg_verify()` compares freshly calculated input checksums against the checksum array carried by the physical extent, offsetting into the original checksum array when the segment is a subrange.
- `vos_csum_recalc_fn()` is the public worker function called by aggregation. It initializes source and destination scatter/gather lists, runs DAOS checksum calculation for each input segment, verifies each input, clears the shared output checksum buffer, and calculates the checksum for the aggregate output extent.

## Control Flow
The caller passes `struct csum_recalc_args` with a BIO sglist, target evtree entry, and per-segment `struct csum_recalc` metadata. `vos_csum_recalc_fn()` allocates a one-iov source SGL and a destination SGL sized to the segment count, creates a `daos_csummer` using the entry checksum type and chunk size, and loops through each input BIO iov. For each segment it checks logical/physical lengths, points the source SGL at the raw buffer and the destination SGL at the requested buffer, computes verification checksum parameters, zeros the checksum buffer, calls `daos_csummer_calc_one()`, and compares against the original physical checksum. Any mismatch returns `-DER_CSUM` and leaves output checksum data zeroed. If all inputs validate, it zeros `ent_in->ei_csum` and calculates output checksums across the destination SGL.

## State And Persistence Behavior
This file does not persist state directly. It mutates the checksum buffers in `evt_entry_in` and `csum_recalc_args`, sets `args->cra_rc`, and uses caller-owned BIO buffers. It intentionally shares the input/output checksum buffer range and clears it before output generation to avoid leaving stale checksum values after verification.

## Dependencies And Integration Points
It depends on DAOS checksum library (`daos_csummer_*`, `csum_chunk_count()`), evtree extent helpers, BIO iov accessors, aggregation data structures from `vos_internal.h`, and DAOS fail injection (`DAOS_VOS_AGG_MW_THRESH`). It is invoked from `vos_aggregate.c` as part of merge-window aggregation.

## Risks And Edge Cases
- Offset math must match checksum chunk boundaries when the output segment covers a subrange of an input physical extent.
- Prefix and suffix lengths must be multiples of record size; assertions catch invalid callers.
- Failure injection can force checksum mismatch when `cr_phy_off` is nonzero.
- The function uses one shared checksum buffer for repeated verification and final output; missing clears would corrupt results.
- Any checksum mismatch aborts output checksum calculation and should propagate to aggregation metrics and error handling.

## Test Signals
Test full-extent verification, subrange verification with nonzero physical offset, merge windows with prefix/suffix records, multi-segment output checksum generation, checksum mismatch returning `-DER_CSUM`, failure-injection mismatch, and allocation failures in source or destination SGL initialization.
