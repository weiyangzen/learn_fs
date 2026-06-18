# sources/object-store/openstack-swift/swift/container/updater.py

## Purpose

`swift/container/updater.py` implements the container-updater daemon. Its job is to scan local container DBs and report changed container statistics to account servers so account listings reflect container existence, object counts, bytes used, delete state, and storage policy. It is the retry path for account updates that failed during direct container-server requests.

## Important APIs, Types, and Functions

`ContainerUpdater(Daemon)` configures storage and ring paths, interval, fork concurrency, rate limiting, timeouts, counters, account suppression settings, DB preallocation, recon cache location, and user agent.

Important methods are `get_account_ring`, `_listdir`, `get_paths`, `_load_suppressions`, `run_forever`, `run_once`, `container_sweep`, `process_container`, `container_report`, and `main`.

## Control Flow

In long-running mode, `run_forever` sleeps for a randomized initial interval, expires old account suppressions, refreshes the account ring, processes partition paths by forked children up to configured concurrency, loads suppression updates from child temp files, logs/writes recon timing, and sleeps the remainder of the interval.

`run_once` avoids forking and processes every path in the current process, then writes recon timing.

`process_container` opens a broker, reads info, skips lock timeouts, skips auto-created containers with non-positive put timestamps, skips suppressed accounts, zeroes object and byte stats for non-root containers, compares current fields against reported fields, and either increments `no_changes` or sends reports to all account replicas. Majority success persists reported fields; all-404 responses quarantine the container DB; other failures suppress the account temporarily.

`container_report` sends a replication-network account `PUT` with timestamps, object count, bytes used, override-deleted, storage policy, and user-agent headers. Connection and response phases have separate timeouts, and errors return a retryable server-error status.

## State and Persistence Behavior

Persistent local state includes broker reported fields, DB quarantine state, and recon cache entry `container_updater_sweep`.

In-memory state includes counters and account suppressions. In `run_forever`, suppressions discovered by children are passed to the parent through temp files that are unlinked after loading.

The account server receives durable account DB updates through replication-network `PUT` requests. For shard containers, object and byte stats are zeroed before reporting to avoid double-counting.

## Dependencies and Integration Points

Dependencies include `ContainerBroker`, `Ring`, `http_connect`, timeout helpers, eventlet spawning and rate limiting, `check_drive`, `DATADIR`, recon helpers, `majority_size`, `Timestamp`, `node_to_string`, and config helpers.

Integration points are direct account updates from the container server, account servers consuming retry reports, sharder/root-container semantics for stat zeroing, and recon tooling.

## Risks and Edge Cases

Forking plus eventlet requires monkey patching in children and in `run_once`. Suppression state is per account and shared from children through temp files; if loading fails, repeated account report attempts may occur sooner than intended.

Majority success is required before reported fields advance. This prevents data loss but can cause repeated reports under partial outages.

All-account-404 handling quarantines the container DB, so false 404s from account-ring or network problems would be severe if every response is misclassified.

Shard container reports zero object/byte stats. Any broker `is_root_container` error could make account stats too low or too high.

The updater skips containers with non-positive put timestamps, so auto-created containers need later real updates before account stats are sent.

## Test Signals

Useful tests should cover path discovery, lazy account-ring loading, skip paths, majority success updating reported fields, partial failures and suppression, all-404 quarantine, non-root stat zeroing, `container_report` headers and error handling, forked suppression loading, recon cache updates, and single-threaded once mode.
