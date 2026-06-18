# sources/distributed-fs/tahoe-lafs/src/allmydata/web/storage.py

## Purpose
Renders the local storage-server status page and JSON status document. It reports disk usage, accepting-shares state, bucket-counter progress, lease-expiration configuration, current and last lease-checker cycle results, corrupt shares discovered by crawlers, and storage nickname/node ID.

## Important APIs, Types, And Functions
`remove_prefix` is a small string helper. `StorageStatusElement` is the main template element with renderers for nickname, node ID, disk stats, accepting state, crawler status, storage-running condition, lease expiration mode/progress/results, and `format_recovered`. `StorageStatus` is a `MultiFormatResource` that renders HTML with `StorageStatusElement` or JSON with stats, bucket-counter state, lease-checker state, and lease-checker progress.

## Control Flow
`root.Root.getChild("storage")` fetches the storage service dynamically and returns `StorageStatus`. HTML rendering reads `storage.get_stats()` repeatedly for disk fields, reads `bucket_counter.get_state()`/`get_progress()`, and reads `lease_checker.get_state()`/`get_progress()` to format current and historical cycle summaries. JSON rendering serializes the same major state objects. Formatting helpers convert byte counts and timings into display strings.

## State And Persistence
The module stores only the storage service reference and nickname. It reads persistent storage-server crawler/lease-checker state but does not mutate it. If the storage server is absent, `StorageStatusElement.storage_running` renders a no-storage message; many other renderers assume `_storage` is not `None` and are therefore template-flow dependent.

## Dependencies And Integration Points
It depends on Twisted templates, Tahoe time/id/json utilities, `abbreviate_space`, and `common.abbreviate_time`/`MultiFormatResource`. It integrates with the storage service API, bucket counter, lease checker, and root dynamic `/storage` child. Tests are concentrated in `src/allmydata/test/test_storage_web.py`.

## Risks And Test Signals
Risks include template renderers dereferencing `_storage` when no storage server is running, assumptions about detailed lease-checker state keys, stale or partial crawler state, and content-type `text/plain` for JSON. Test signals should cover storage absent/present paths, all disk stat fields including `None`, accepting immutable shares, bucket counter progress states, lease expiration modes (`age`, `cutoff-date`), current-cycle and last-cycle summaries, corrupt share lists, and JSON serialization of stats/crawler state.
