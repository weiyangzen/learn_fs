# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zio_inject.c

## Purpose

`zio_inject.c` implements ZFS fault injection support used by `zinject` and test code. It registers fault handlers, matches them against logical or device I/O, injects errors/delays/panics/ignored writes, translates byte ranges to block ranges, lists/clears handlers, and initializes/finalizes global injection state.

## Major Responsibilities

- Maintains a global list of `inject_handler_t` records.
- Tracks whether injection is enabled with `zio_injection_enabled`.
- Supports data, device, label, decrypt, delay, panic, and ignored-write injection commands.
- Matches logical block bookmarks, object types, DVA masks, vdev GUIDs, I/O types, and error classes.
- Converts user byte ranges into block IDs through dnode metadata.
- Keeps an injection reference on the target SPA while a handler exists.
- Provides listing and clearing APIs for registered handlers.
- Flushes ARC when requested so reads reach the ZIO layer.

## Data Structures

`inject_handler_t` stores:

- Unique handler ID.
- Held `spa_t`.
- `zinject_record_t` rule.
- Optional delay lanes array.
- Next delay lane index.
- List node.

Global state:

- `inject_handlers`: all active handlers.
- `inject_lock`: protects handler list and delay handler count.
- `inject_delay_count`: count of active delay handlers.
- `inject_delay_mtx`: serializes delay lane assignment.
- `inject_next_id`: monotonic handler ID source.

## Matching

`freq_triggered()` implements probabilistic injection. Frequency `0` means always. Legacy 0-100 percentages and scaled `ZI_PERCENTAGE_MAX` values are both supported.

`zio_match_handler()` matches either MOS metadata by object type or exact bookmark ranges by objset, object, level, block ID range, DVA mask, and error.

`zio_match_dva()` identifies which DVA a vdev child I/O corresponds to by matching top vdev and offset, compensating for leaf label offset.

## Injection Paths

`zio_handle_panic_injection()` panics when a matching SPA, function tag, and type are found.

`zio_handle_decrypt_injection()` injects decrypt/authentication failures for matching bookmarks and object types.

`zio_handle_fault_injection()` injects logical data faults, currently only for reads with logical data.

`zio_handle_label_injection()` injects faults into vdev label regions, translating relative label offsets into physical label offsets.

`zio_handle_device_injection()` injects device-level faults by vdev GUID. It can skip label regions, respect failfast semantics, filter by I/O type, set `VDEV_AUX_OPEN_FAILED` for `ENXIO`, and mark retried I/O for statistics/FMA behavior.

`zio_handle_ignored_writes()` simulates hardware ignoring writes by removing vdev I/O stages from some syncing txg writes for a configured duration.

`spa_handle_ignored_writes()` validates ignored-write injection duration during spa sync.

`zio_handle_io_delay()` computes a target completion time for delayed I/O using per-handler lanes, frequency, vdev GUID, and configured latency.

## Delay Injection

Delay handlers have a fixed latency and lane count. Each lane records when it becomes idle. `zio_handle_io_delay()` chooses the handler/lane that can complete soonest, updates that lane atomically under `inject_delay_mtx`, and returns the target timestamp. `zio_delay_interrupt()` in `zio.c` uses this timestamp to delay completion.

The code rejects zero delay, zero lanes, and very large lane counts at registration.

## Registration and Clearing

`zio_inject_fault()` optionally unloads the SPA, optionally translates byte ranges, obtains an injection SPA reference, allocates a handler, allocates delay lanes if needed, inserts the handler under writer lock, increments enabled counters, and optionally flushes ARC.

`zio_inject_list_next()` returns the first handler with ID greater than the supplied ID and copies the pool name and record.

`zio_clear_fault()` removes a handler by ID, updates delay counts, frees delay lanes, releases the SPA injection reference, frees the handler, and decrements `zio_injection_enabled`.

`zio_inject_init()` initializes locks and the handler list. `zio_inject_fini()` destroys them.

## Key Dependencies

- `zio.c` calls injection hooks from checksum verification, vdev completion, vdev assessment, decryption, and ready stages.
- SPA namespace/injection references prevent disappearing pools while handlers exist.
- ARC flush is used to force subsequent reads through the ZIO layer.
- Dnode/dataset APIs translate byte ranges to block ranges.

## Notes for Future Readers

- The handler list is intentionally simple because few active faults are expected.
- Delay lane assignment requires both reader lock on the handler list and a mutex for per-lane atomicity.
- Device injection treats `ENXIO` specially and may convert it to `EIO` for active I/O.
- Logical data injection only applies to reads.
