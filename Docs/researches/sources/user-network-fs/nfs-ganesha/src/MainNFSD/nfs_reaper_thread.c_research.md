# sources/user-network-fs/nfs-ganesha/src/MainNFSD/nfs_reaper_thread.c

## Purpose

This file implements the NFSv4 reaper looper. Its job is to periodically expire stale NFSv4 client IDs, reap delayed client cleanup lists, release cached open owners after their close-pending grace window, and optionally call `malloc_trim` to reduce heap fragmentation.

The reaper is implemented as a `fridgethr` single-thread looper named `reaper`. It is part of MainNFSD lifecycle startup/shutdown and maintains NFSv4 lease health by walking confirmed and unconfirmed client-id hash tables.

## Important APIs, types, and functions

`reaper_init` creates and starts the looper. `reaper_wake` wakes it early if `reaper_fridge` exists. `reaper_shutdown` stops it with a 120-second sync command and cancels on timeout.

`reaper_run` is the periodic worker callback. It invokes `nfs_maybe_start_grace`, tries to lift grace with `nfs_try_lift_grace` unless `admin_shutdown` is set, logs state dumps in debug builds, reaps delayed cleanup, walks both client-id hash tables, reaps expired open owners, and optionally trims malloc fragmentation.

`reap_hash_table` iterates a `hash_table_t` partition-by-partition, takes each partition write lock, walks the red-black tree, checks each `nfs_client_id_t` under `cid_mutex`, skips valid leases and already delayed cleanup, references the client id, drops the partition lock, expires the client with `nfs_client_id_expire`, and restarts the current partition walk because expiration may mutate the tree.

`reap_expired_open_owners` walks the global `cached_open_owners` list under `cached_open_owners_lock`, stops at the first non-expired owner because the list is ordered by expiration, and calls `uncache_nfs4_owner` for expired entries.

On non-Apple platforms, `get_current_rss` reads `/proc/self/statm` and `reap_malloc_frag` calls `malloc_trim(0)` when current RSS exceeds a dynamic threshold derived from `nfs_param.core_param.malloc_trim_minthreshold`.

## Control flow

Initialization sets `reaper_delay` to the default 10 seconds unless the NFSv4 lease lifetime is less than 20 seconds, in which case it uses half the lease lifetime. `reaper_init` fills `fridgethr_params` with one minimum and maximum thread, `fridgethr_flavor_looper`, and the selected delay, initializes the fridge, and submits `reaper_run` with `reaper_state`.

Each `reaper_run` tick first manages grace-period state. It then logs a "checking clients" message only when prior work was nonzero or the message has not been logged yet, with optional SAL state dumps when `DEBUG_SAL` is enabled and the previous count was zero.

Client expiration first drains `reap_expired_client_list(NULL)`, then `reap_hash_table(ht_confirmed_client_id)`, then `reap_hash_table(ht_unconfirmed_client_id)`. Inside `reap_hash_table`, if an expired client is found, the function obtains a client-id reference, releases the partition lock, locks the client record, expires the client, unlocks, drops the reference, and restarts the partition from the root. This avoids continuing an iterator across a tree modified by expiration.

Open-owner reaping follows client-id reaping. It repeatedly inspects the first cached owner and stops as soon as it sees a future expiration time, relying on insertion/order semantics of `cached_open_owners`.

Shutdown sends `fridgethr_comm_stop`. If that times out, the reaper fridge is canceled. Other nonzero return codes are logged and returned to the caller.

## State and persistence behavior

The file owns `reaper_delay`, `reaper_fridge`, and `reaper_state`. `reaper_state.count` carries the amount of work from the previous run for logging decisions, and `reaper_state.logged` suppresses repetitive idle debug logs.

Persistent server state is external: confirmed/unconfirmed client-id hash tables, the expired client list, cached open-owner list, grace-period flags, client records, and global NFS parameters. The reaper mutates those external structures by expiring clients, uncacheing owners, and potentially triggering delayed cleanup paths.

Memory trimming state is maintained in a static `trim_threshold` inside `reap_malloc_frag`. It starts at the configured minimum, drops if current RSS is much lower, and after trimming becomes 1.5x the current RSS or the configured minimum.

## Dependencies and integration points

This file depends on `fridgethr`, NFSv4 state and lease APIs (`valid_lease`, `nfs_client_id_expire`, `inc_client_id_ref`, `dec_client_id_ref`, `display_client_id_rec`), SAL state owner APIs (`cached_open_owners`, `uncache_nfs4_owner`, `display_owner`), NFS core parameters, logging, pthread locks, and hash-table/red-black tree internals.

It integrates directly with NFSv4 grace handling (`nfs_maybe_start_grace`, `nfs_try_lift_grace`) and the global shutdown flag (`admin_shutdown`). The `/proc/self/statm` and `malloc_trim` path is Linux/glibc-oriented and compiled out on Apple.

## Risks and edge cases

The hash-table reaper intentionally drops and reacquires locks during expiration, so restart behavior is essential. Removing the `goto restart` pattern or keeping iterators across expiration would risk use-after-free or missing entries.

`reap_hash_table` takes partition write locks even though it is scanning, because expiration can mutate table state. This can block client-id operations; long expiration work is therefore moved outside the partition lock, but the per-partition restart can be expensive if many clients expire.

The open-owner cache assumes entries are ordered by expiration and not moved while cached. If that invariant breaks, `reap_expired_open_owners` can leave expired owners behind after the first future-dated entry.

`reaper_delay` can become zero if lease lifetime is less than two seconds because integer division is used. The surrounding configuration likely prevents such a lease value, but validation should ensure the looper delay remains usable.

`get_current_rss` returns zero on several failures. `reap_malloc_frag` treats zero as a very low RSS and may adjust thresholds downward; logs help identify `/proc` parsing failures but the behavior is intentionally nonfatal.

## Test signals

Useful tests include hash tables containing valid, expired, delayed-cleanup, confirmed, and unconfirmed clients; expiration paths that mutate the table; delayed cleanup list saturation; cached open owners ordered by expiration; early wake behavior; shutdown timeout behavior; and `malloc_trim` threshold evolution with mocked RSS.

Integration signals are logs showing grace lift attempts, client expiration counts, no leaked client references, no partition-lock deadlocks, and timely removal of expired owners. Stress tests should create many client IDs expiring at once and verify the restart loop terminates and the server remains responsive.
