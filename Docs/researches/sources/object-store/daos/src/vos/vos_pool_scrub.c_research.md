# sources/object-store/daos/src/vos/vos_pool_scrub.c

## Purpose
`vos_pool_scrub.c` implements checksum scrubbing for all containers in a VOS pool. It schedules scrub passes based on pool properties, waits for containers to have checksum state loaded, iterates object values, recomputes checksums chunk-by-chunk, marks corrupt records, emits telemetry/RAS signals, and can drain a target after too many corruptions.

## Important APIs, Types, And Functions
The main entry point is `vos_scrub_pool`. Supporting functions include `sc_should_start`, `sc_ensure_containers_are_loaded`, `sc_scrub_cont`, `obj_iter_scrub_pre_cb`, `sc_verify_obj_value`, `sc_verify_recx`, `sc_verify_sv`, `sc_handle_corruption`, `sc_mark_corrupt`, `sc_pool_drain`, and `get_ms_between_periods`. State is carried in `struct scrub_ctx`, including pool properties, metrics, current object/key/value coordinates, checksum to verify, VOS iterator handle, scheduler callbacks, and container callbacks.

## Control Flow
`vos_scrub_pool` exits early if the pool handle is invalid or scrub should not start. When starting, it ensures containers are loaded, records metrics, iterates container UUIDs, opens each container through callbacks, and runs object iteration with `obj_iter_scrub_pre_cb`. The object callback skips already-seen positions across yields, sets up IOD and checksum context for single values or recxs, reads media into a temporary buffer, verifies checksums, yields/sleeps between chunk calculations, and handles corruption before continuing.

## State And Persistence
Most state is runtime telemetry and iterator progress in `scrub_ctx`. Persistent effects occur when corruption is marked via `vos_iter_process(..., VOS_ITER_PROC_OP_MARK_CORRUPT, ...)`, which updates durable record address flags in the iterator implementation. RAS events and BIO checksum error logging provide external signals; metrics count scrub passes, bytes, checksum calculations, corruptions, duration, and idle/busy time.

## Dependencies And Integration Points
The module integrates with DAOS checksum APIs, server checksum setup, VOS pool/container/object iterators, media reads, BIO NVMe error logging, RAS, DAOS telemetry, pool property scrub mode/frequency/threshold, and scheduler sleep/yield callbacks. It relies on container lookup/put callbacks supplied by the server layer.

## Risks
Risks include validating an iterator position after yielding before marking corruption, correctly handling deleted containers/values, avoiding infinite waits for unloaded containers, respecting pool/container stopping conditions, and preserving fairness in timed/lazy modes. Memory allocation for data buffers and checksum buffers is per-value/chunk and must unwind cleanly. Corruption threshold handling returns shutdown after attempting drain.

## Test Signals
Tests should cover disabled/off scrub, lazy mode idle gating, timed spacing from `get_ms_between_periods`, unloaded container waiting, container deletion during scrub, existing corrupted records on first pass, SV and recx checksum mismatch marking, NVMe vs SCM behavior, corruption threshold drain, stop flags, and overlapping extent checksum visibility limitations noted by the FIXME.
