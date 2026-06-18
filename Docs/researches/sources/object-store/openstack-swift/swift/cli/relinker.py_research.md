# sources/object-store/openstack-swift/swift/cli/relinker.py

## Purpose
`relinker.py` implements `swift-object-relinker`, the operational tool used during object-ring partition-power increases. It runs in two phases: `relink` creates hard links from old partition directories into the next partition-power layout, and `cleanup` removes old files after the ring has been advanced and the new layout is authoritative.

## Important APIs, types, and functions
- Constants define lock/state filenames, phase names, exit codes, and the default recon update interval.
- `policy()` resolves CLI policy names or indexes through `POLICIES`.
- `_aggregate_stats()`, `_aggregate_recon_stats()`, `_zero_stats()`, and `_zero_collated_stats()` shape per-policy, per-device, and worker recon data.
- `Relinker` owns traversal, per-device locking, state-file resume, diskfile operations, recon updates, and final status.
- `Relinker.devices_filter()`, `partitions_filter()`, `hashes_filter()`, and hook methods plug into `audit_location_generator`.
- `Relinker.do_relink()` wraps `diskfile.relink_paths()` and handles hardlink collisions, tombstone special cases, quarantine retry, and cleanup tolerance.
- `Relinker.process_location()` compares old and new hash directories, creates missing required links, removes old files in cleanup mode, and invalidates suffix hashes.
- `parallel_process()` resets recon state, splits devices across forked workers, waits for child exit statuses, and maps failures to tool exit codes.
- `main()` merges config-file and CLI options, sets the eventlet hub, optionally drops privileges, builds the relinker config, and starts `parallel_process()`.

## Control flow
The CLI accepts an `action` of `relink` or `cleanup`, optional object-relinker config, policy/device/partition filters, rate limits, worker count, logging/debug flags, and hardlink-collision policy. `parallel_process()` clears the previous recon file, chooses worker count (`auto` means one worker per device), then either runs one `Relinker` inline or forks workers with evenly distributed device lists.

Each worker iterates selected storage policies. It reloads the object ring and only processes policies whose `next_part_power` state matches the requested phase: during `relink`, `next_part_power` differs from `part_power`; during `cleanup`, the ring has already advanced so they match. For each policy, `audit_location_generator()` walks devices, partitions, suffixes, and hash dirs. Pre-device hooks take an exclusive `.relink.<datadir>.lock`, read `relink.<datadir>.json` if compatible, and initialize recon progress. Partition filtering excludes upper-half partitions that do not need work for the current phase, resumes incomplete partition states, and scans in reverse partition order to reduce unnecessary reads.

For every mismatched hash path, `process_location()` cleans both target and source on-disk file sets, computes the newest required files with the diskfile manager, drops obsolete entries, then ensures every required source file is linked to the target. In cleanup mode, old files are removed only if every required link was verified. Post-partition hooks invalidate affected hashes, opportunistically remove empty old partition directories during cleanup, and atomically persist state by writing and fsyncing a temp JSON file before rename.

## State and persistence behavior
This file mutates object storage paths directly through hard links and deletes. Per-device progress is persisted in `relink.<datadir>.json` so interrupted runs resume partition-by-partition. The lock file serializes work per device/datadir. Recon cache state is periodically dumped to `RECON_RELINKER_FILE`, including worker liveness, per-device policy progress, timestamps, totals, and return codes. Cleanup can delete old object files and empty partitions, while relink may quarantine colliding target files when `clobber_hardlink_collisions` is enabled.

## Dependencies and integration points
The tool depends on Swift storage policies, object rings, `DiskFileRouter`, diskfile hash invalidation/cleanup/linking/quarantine helpers, `audit_location_generator`, rate limiting, recon cache dumping, privilege dropping, logging adapters, eventlet hub setup, and ring partition-path utilities. It is tightly coupled to `swift-ring-builder` partition-power commands: operators prepare the ring, run relink across object servers, increase partition power, deploy the ring, run cleanup, then finish the increase.

## Risks and edge cases
The phase predicates must match ring rollout order; running cleanup before all servers use the advanced ring can remove live old-path data. Hardlink collisions are dangerous because target and source may contain different inodes for the same timestamp; tombstone collisions are tolerated, optional clobbering quarantines target files during relink, and cleanup favors the new location. State-file compatibility checks protect against using stale progress after ring power changes, but corrupt state files are removed and the scan restarts. Hash invalidation failures are logged without counting as hard errors after a link is already created, leaving replication or periodic rehash to recover. Device mount/list errors are aggregated into non-zero exits even if traversal itself logs them as warnings.

## Test signals
Useful tests should cover phase filtering for `part_power`/`next_part_power`, state-file resume and invalidation, per-device locking, partition scan filtering, relink idempotence, cleanup idempotence, hardlink collision modes, tombstone collision tolerance, suffix invalidation failures, unmounted or unlistable devices, worker aggregation, and recon output. Integration tests need realistic object diskfile layouts and ring transition sequencing because correctness depends on filesystem semantics and operational ordering.
