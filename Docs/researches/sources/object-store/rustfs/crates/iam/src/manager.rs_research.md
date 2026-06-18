# sources/object-store/rustfs/crates/iam/src/manager.rs

## Purpose

`manager.rs` is the high-level IAM cache and mutation coordinator. It wraps a pluggable `Store` backend, keeps an in-memory `Cache` coherent with persisted IAM objects, performs initial and periodic reloads, exposes policy/user/group/service-account operations to admin and auth paths, and handles notification-driven cache refreshes. The file is the boundary where persisted IAM documents become fast authorization state.

## Important APIs, Types, and Functions

`IamState` tracks `Uninitialized`, `Loading`, `Ready`, and `Error` states. `IamCache<T: Store>` owns the backend `api`, the shared `cache`, background reload channel, role map, timestamp, and sync metrics counters. `IamSyncMetricsSnapshot` exposes reload duration, age, success count, and failure count.

Construction flows through `IamCache::new()` and `init()`. `init()` persists the IAM format file, retries full load three times, sets state to `Ready` or `Error`, then optionally spawns a 120-second reload loop unless `RUSTFS_SKIP_BACKGROUND_TASK` is set. `_notify()` sends timestamps to that loop, and `load()` calls `Store::load_all()`, updates `last_timestamp`, and records metrics.

Read APIs include `is_ready`, `get_user`, `get_mapped_policy`, `get_policy`, `get_policy_doc`, `list_polices`, `list_policy_docs`, `list_policy_docs_internal`, `merge_policies`, `list_temp_accounts`, `list_sts_accounts`, `list_service_accounts`, `get_user_info`, `get_users`, `get_bucket_users`, `get_users_with_mapped_policies`, `policy_db_get`, `is_temp_user`, `get_group_description`, `list_groups`, and `update_groups`.

Mutation APIs include `set_policy`, `delete_policy`, `add_user`, `delete_user`, `update_user_secret_key`, `add_user_ssh_public_key`, `set_user_status`, `add_service_account`, `update_service_account`, `set_temp_user`, `policy_db_set`, `add_users_to_group`, `set_group_status`, `remove_members_from_group`, and `remove_users_from_group`. Notification handlers (`group_notification_handler`, `policy_notification_handler`, `policy_mapping_notification_handler`, `user_notification_handler`) reconcile cache state after external changes.

Helper functions cover format path building, default canned policy injection, token signing key retrieval, JWT claim extraction with and without required `exp`, policy filtering, and group-description construction.

## Control Flow

Initial startup writes `config/iam/format.json` via `save_iam_formatter()`, but only the first local cluster node writes if the file is missing or older than version 1. Full reload delegates to `Store::load_all()` and only marks the system ready after a successful cache replacement. Later reloads are ticker-driven or channel-driven; channel timestamps older than `last_timestamp` are ignored.

Most mutating methods validate inputs, persist through `Store`, and then update cache with an `OffsetDateTime::now_utc()` timestamp. This makes persistent success the normal prerequisite for in-memory visibility. Several paths intentionally tolerate missing secondary data: missing mapped policies are often treated as empty, while unexpected backend errors propagate.

Policy resolution starts from a comma-separated `MappedPolicy`, loads missing docs lazily when possible, and merges concrete `Policy` values with `Policy::merge_policies`. Bucket-scoped list operations call asynchronous `match_resource()` for each policy document and filter results.

User deletion has cascading behavior. Deleting a regular user first removes group memberships, then deletes child service accounts and STS/temp accounts from the store and cache. User notification deletion mirrors this cascade when a regular user disappears elsewhere.

Group membership operations maintain both `groups` and the reverse `user_group_memberships` map. Group deletion is represented by calling `remove_users_from_group()` with an empty member list; this refuses to delete non-empty groups, deletes group policy mapping, deletes group info, and removes reverse memberships.

## State and Persistence Behavior

The manager does not directly serialize IAM records except for the format marker. It persists users, groups, policies, policy mappings, and temporary accounts through `Store`. Cache updates are granular for single-object operations and wholesale for `load_all()`.

`load_user()` is a targeted cache warmup path. It tries service accounts first, loads parent regular policy when relevant, otherwise tries regular and STS identities, loads STS parent mapped policies, and pulls referenced policy docs before writing all gathered objects into cache.

`update_service_account()` mutates service-account metadata and session policy by decoding the existing session JWT with either the current secret or missing-exp allowance, adjusting claims, enforcing `MAX_SVCSESSION_POLICY_SIZE`, and resigning the token with the selected secret.

`policy_db_get_internal()` combines direct user policies with group policies from credentials groups and cache-built memberships. A disabled group currently causes an early empty result for the user path, which is a behavior to watch because one disabled group can suppress otherwise valid policies.

## Dependencies and Integration Points

The file depends on the local `Cache`, `Store`, error helpers, IAM sys constants, and object-store IAM prefix. External integration includes `rustfs_credentials`, `rustfs_policy` for policy/user/JWT primitives, `rustfs_madmin` admin DTOs, `rustfs_ecstore::global::is_first_cluster_node_local`, `rustfs_utils` env/path helpers, `tokio` for async background work, `futures::join_all`, and `tracing`.

It is consumed by admin handlers, STS flows, auth code that resolves users and policies, notification/watch paths, and the object-backed store implementation. `extract_jwt_claims*` also ties the manager to global action credentials.

## Risks and Edge Cases

`_notify()` unwraps channel send and can panic if the receiver is closed. Background reload errors are logged but do not downgrade `IamState`, so `is_ready()` may stay true after repeated reload failures.

Several lazy loads ignore missing policies by design, but missing or stale cache entries can temporarily produce empty authorization sets. `filter_policies_from_docs()` uses `pollster::block_on()` inside a synchronous helper, which can be risky if `match_resource()` ever requires an async runtime interaction that should not be blocked.

`delete_policy()` has surprising error handling: in the `is_from_notify` branch, a delete error that is not `NoSuchPolicy` removes the cache entry and returns `Ok`, while `NoSuchPolicy` is returned as an error. This may be intentional notification semantics, but it deserves review.

Service-account update depends on decoding the existing JWT before changing the secret. Expiration validation is marked TODO. Policy and group ordering is mostly HashSet-derived, so returned comma strings and member lists may be nondeterministic.

## Test Signals

Tests cover initial load failure preserving `Error` state and recording three failures, IAM format serialization/path helpers, default policy construction, JWT extraction failure paths, empty policy filtering, mapped policy behavior, user/policy/group data shape, status/session constants, credential validation, policy merge, and disabled group description preserving policy. These tests give useful regression signals for initialization, serialization, and helpers, but they do not exercise real object-store persistence, background reload races, notification cascades, or most mutating admin flows.
