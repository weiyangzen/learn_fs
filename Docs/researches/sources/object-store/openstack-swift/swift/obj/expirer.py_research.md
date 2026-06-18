# sources/object-store/openstack-swift/swift/obj/expirer.py

## Purpose
`expirer.py` implements Swift's object-expirer daemon and shared expirer configuration helpers. It scans hidden expiring-object task containers, determines which expiration tasks are due, rate-limits and parallelizes deletion of target objects, and removes completed task entries from the queue. It also supports legacy queue configuration, process sharding, delayed reaping for selected accounts or containers, async-delete task entries, recon reporting, and task-container naming.

## Important APIs, Types, And Functions
`ExpirerConfig` normalizes expirer account and container settings. It handles deprecated `expiring_objects_container_divisor` and `expiring_objects_account_name`, computes deterministic task container names with `get_expirer_container()`, validates task-container timestamps with `is_expected_task_container()`, and returns container-ring nodes with `get_delete_at_nodes()`.

`build_task_obj()` and `parse_task_obj()` encode and decode queue object names in `<timestamp>-<account>/<container>/<object>` format. `extract_expirer_bytes_from_ctype()` and `embed_expirer_bytes_in_ctype()` store object byte counts in task content types for queue monitoring. `read_conf_for_delay_reaping_times()` parses `delay_reaping_<account>` and `delay_reaping_<account>/<container>` config keys, while `get_delay_reaping()` resolves the account/container-specific delay.

`ObjectExpirer` is the daemon. Its constructor reads interval, task rate, concurrency, reclaim age, queue access, internal client, recon paths, and round-robin cache size. `_make_internal_client()` builds an `InternalClient` on the replication network. `read_conf_for_queue_access()` and `_validate_processes_config()` manage legacy queue access and process sharding.

Task discovery APIs include `iter_task_accounts_to_expire()`, `get_task_containers_to_expire()`, `_iter_task_container()`, `iter_task_to_expire()`, `round_robin_order()`, and `hash_mod()`. Execution APIs include `run_once()`, `run_forever()`, `delete_object()`, `delete_actual_object()`, `pop_queue()`, and `report()`. `main()` exposes `--processes` and `--process` CLI overrides.

## Control Flow
On startup, the daemon creates or receives an internal Swift client, determines whether the configured file is legacy `object-expirer.conf`, and decides whether to dequeue from the legacy `.expiring_objects` account. `run_forever()` sleeps a randomized initial offset, then repeatedly calls `run_once()` and sleeps a randomized remainder of `interval`.

`run_once()` validates command-line process overrides, exits early if this node is not configured to dequeue legacy tasks, creates a `GreenPool`, and iterates task accounts. For each task account, it fetches account info. If containers exist, it lists candidate task containers via `get_task_containers_to_expire()`, which stops once task-container timestamps are in the future and logs unexpected container names.

For each due task container, `_iter_task_container()` lists queue objects, parses the task object name, identifies async-delete tasks by content type, applies due-time checks and configured delayed reaping, assigns work to only one process via `hash_mod(task_container/task_object) % divisor`, and yields task dictionaries. Empty task containers are deleted. `iter_task_to_expire()` catches listing errors so one bad container does not abort the pass.

The yielded tasks are passed through `round_robin_order()` to avoid long runs against one target container, then through `RateLimitedIterator` to cap task starts per second. Each task is spawned into the green pool as `delete_object()`. That method calls `delete_actual_object()` with either async-delete headers or normal expiration headers (`X-If-Delete-At` and no queue cleaning by the object server), handles retryable responses, pops the queue entry with `direct_delete_container_entry()` after success or acceptable terminal outcomes, increments metrics, and reports progress.

## State, Persistence, And Dependencies
The expirer queue is persisted as Swift objects under the auto-created `.expiring_objects` account. Task containers are timestamp buckets, with a hash-derived offset to spread load across `EXPIRER_CONTAINER_PER_DIVISOR` shard containers per divisor window. Task object names contain the target path and delete timestamp. Task object content type can distinguish normal expiration from async delete and can embed byte-count metadata.

The daemon itself persists only recon metrics through `dump_recon_cache()` under `RECON_OBJECT_FILE`. It relies on the Swift cluster for queue persistence, target object state, and direct container-entry deletion. Runtime state includes report counters, process-sharding indexes, delay-reaping mappings, and round-robin caches.

Dependencies include `InternalClient`, Swift container-ring direct deletion, `split_path`, normalized timestamps, `RateLimitedIterator`, eventlet `GreenPool` and `sleep`, recon helpers, common HTTP status constants, and Swift config parsing helpers. The queue account prefix comes from `AUTO_CREATE_ACCOUNT_PREFIX`, so operators should not independently change it.

## Integration Points
Proxy and object-server paths that create expiring objects use `ExpirerConfig`, `build_task_obj()`, and task-container calculations to enqueue expiration work consistently. The expirer daemon consumes that queue through `InternalClient`, deletes target objects through normal Swift object DELETE calls, and removes queue entries directly from container servers. Recon tooling reads `object_expiration_pass` and `expired_last_pass`.

The daemon integrates with object-server expiration semantics through headers. Normal expiration sends `X-If-Delete-At` to ensure only the matching scheduled object is deleted and sets `X-Backend-Clean-Expiring-Object-Queue: no` so the object server does not also clean the queue. Async delete uses a different content type and looser acceptable statuses.

## Risks
Queue naming and timestamp normalization must remain compatible across proxy, object server, and expirer. Changing divisor or account settings can orphan tasks; the code warns about deprecated settings but still supports them. `parse_task_obj()` assumes task names contain the expected `-` separator and valid Swift path; malformed tasks are logged and skipped, potentially leaving bad queue entries.

Deletion retry behavior is intentionally conservative. Recent `404` or precondition failures are retried until `reclaim_age` passes, while older failures may allow queue removal. Incorrect handling can either leak queue tasks forever or remove tasks before an object is actually expired. Process sharding depends on consistent md5 modulo inputs; any change can duplicate or skip work during rolling upgrades.

Delayed reaping configuration is path-sensitive and percent-decoded. Invalid keys raise during startup. The round-robin cache can grow up to `round_robin_task_cache_size`, so very large settings trade memory for fairness. Direct queue popping bypasses proxy paths and assumes container-ring access is correct.

## Test Signals
Tests should cover task object build/parse round trips, expirer container calculation and expected-container validation, deprecated config warnings, invalid divisor/account behavior, delay-reaping parsing and lookup, content-type byte embedding/extraction, process-shard assignment, future task/container skipping, async-delete classification, empty-container deletion, round-robin fairness, rate-limited spawning, normal delete headers, async-delete headers, retry behavior for `404`, `409`, and precondition failures, queue popping, recon reporting, and CLI process override validation.

No local tests were present under this vendored source tree, so these signals are inferred from function boundaries and Swift's object-expirer behavior.
