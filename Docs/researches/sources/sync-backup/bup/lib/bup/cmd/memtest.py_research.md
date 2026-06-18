# sources/sync-backup/bup/lib/bup/cmd/memtest.py

## Purpose
`memtest.py` measures memory and lookup costs for pack index, midx, and bloom lookup paths by repeatedly testing object existence.

## APIs and Control Flow
`linux_memstat` optionally reads `/proc/self/status`. `report(count, out)` emits RSS, major faults, user/sys milliseconds, and elapsed milliseconds while updating global timing baselines. `main(argv)` rejects arguments, opens a `PackIdxList`, writes a header, warms random SHA generation, then for each cycle tests either real objects from an infinite iterator or random non-existing SHA values. It prints aggregate bloom/midx/idx search counters and total time.

## State, Dependencies, Integration, Risks, Tests
State is process-local globals for timing and search counters in imported modules. It persists nothing. Dependencies are Linux `/proc`, `resource.getrusage`, `_helpers.random_sha`, and pack index structures. Risks include platform-specific RSS units, infinite iterator assumptions when `--existing` has no objects, and assertions relying on negligible random SHA collisions. Test signals include output schema, `--existing` behavior, `--ignore-midx`, cycle/number handling, and graceful missing `/proc` warning once.
