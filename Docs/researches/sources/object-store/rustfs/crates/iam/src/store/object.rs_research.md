# sources/object-store/rustfs/crates/iam/src/store/object.rs

## Purpose

`store/object.rs` is the object-backed implementation of the IAM `Store` trait. It stores IAM metadata in the `.rustfs.sys` system bucket under `config/iam`, handles encrypted and legacy plaintext/encrypted config formats, lists IAM object trees, loads records concurrently during full reload, and writes the final cache snapshot used by the IAM manager.

## Important APIs, Types, and Functions

The file defines public `LazyLock<String>` prefixes for IAM root, users, service accounts, groups, policies, STS users, and policy DB subtrees. Path helpers build canonical object keys for identity (`identity.json`), policy (`policy.json`), group members (`members.json`), and mapped policy JSON files.

`ObjectStore` wraps `Arc<ECStore>` and implements `Store`. Public construction is `ObjectStore::new()`. `StringOrErr` is used by listing channels to stream either discovered object names or errors.

Encryption helpers are central: `decrypt_data_with_source()` accepts plaintext JSON, current IAM master-key stream encryption, old master keys, legacy secret-key encryption, and legacy `access:secret` stream encryption. `prepare_data_for_storage()` encrypts with the configured IAM master key when present, otherwise stores plaintext. `should_lazy_rewrite()`, `begin_lazy_rewrite()`, `complete_lazy_rewrite()`, `maybe_schedule_lazy_rewrite()`, and `lazy_rewrite_iam_config()` opportunistically rewrite plaintext or old-key data using the current master key with ETag preconditions.

Listing/loading helpers include `split_path`, `list_iam_config_items`, `list_all_iamconfig_items`, `load_policy_doc_concurrent`, `load_user_concurrent`, `load_mapped_policy_internal`, `load_mapped_policy_concurrent`, and `check_storage_readiness`.

## Control Flow

Generic `load_iam_config()` reads object data with metadata, decrypts it, schedules a lazy rewrite if appropriate, and deserializes JSON. Decrypt failure is logged and returned as `ConfigNotFound` while preserving the object. `save_iam_config()` serializes JSON, applies encryption if configured, and retries `save_config()` up to five times with exponential backoff. `delete_iam_config()` delegates to `delete_config()`.

User loading normalizes missing access keys to the object name, deletes expired identities and their mapped policy, and extracts JWT claims for session-token credentials. Service accounts without expiration use the missing-exp claim extractor. If claim extraction fails for temporary credentials, the temp identity and mapped policy are deleted.

List methods walk a prefix in `.rustfs.sys`, normalize Windows separators, strip the prefix, and stream names through a bounded channel. `list_all_iamconfig_items()` walks the IAM root once, classifies entries by top-level prefix, and uses a last-slash split for `policydb/*` entries so policy mapping files are grouped correctly.

`load_all()` is the full cache hydration path. It lists all IAM config objects, starts with default canned policies, loads policy docs and regular users in batches of 32 concurrent futures, loads groups and group policies, loads user mapped policies, loads service accounts into the user cache, loads STS parent policies for service accounts whose parent is not a regular user, loads STS identities and STS mapped policies, and finally replaces cache entities only if the cache still matches the snapshot captured at start. If concurrent cache mutations occurred, the full reload commit is skipped with a warning.

## State and Persistence Behavior

Persistent IAM state lives under `.rustfs.sys/config/iam`: regular users under `users/<name>/identity.json`, service accounts under `service-accounts/<name>/identity.json`, STS under `sts/<name>/identity.json`, groups under `groups/<name>/members.json`, policies under `policies/<name>/policy.json`, and mapped policies under `policydb/users`, `policydb/sts-users`, `policydb/service-accounts`, or `policydb/groups`.

The store preserves backward compatibility with plaintext JSON and legacy encryption. When a current IAM master key is configured, old formats are lazily rewritten after reads. Rewrites are protected by a global `IAM_LAZY_REWRITE_TRACKER` to avoid duplicate rewrites and by object ETag `If-Match` preconditions to avoid overwriting newer data. Failed rewrites enter a 60-second cooldown.

`load_policy()` fills `create_date` and `update_date` from object modification time when loading version-0 policy documents. Full reload defaults include canned policies even when no policy objects exist.

## Dependencies and Integration Points

This module integrates with `rustfs_ecstore` config helpers (`read_config_with_metadata`, `read_config_no_lock`, `save_config`, `save_config_with_opts`, `delete_config`), object walking, `ECStore`, `ObjectOptions`, and HTTP preconditions. It records system-path failures through `rustfs_io_metrics` and classifies failures through `rustfs_ecstore::error`.

It depends on IAM `Cache`/`CacheEntity`, errors, keyring, manager JWT helpers/default policies, `rustfs_crypto`, `rustfs_credentials`, `rustfs_policy`, `tokio` channels/spawn, cancellation tokens, `join_all`, and tracing. `manager.rs` relies on this implementation for startup load, targeted cache repair, and all IAM persistence.

## Risks and Edge Cases

`check_storage_readiness()` requires `format.json` to exist before saving identities. This protects boot-time writes but can block writes if format initialization failed or if a deployment intentionally lacks the probe object.

`load_iam_config()` maps decrypt failures to `ConfigNotFound`, which prevents deletion but can make corruption indistinguishable from absence to callers. Some higher-level paths then convert that to `NoSuchUser` or `NoSuchPolicy`.

`save_iam_config()` increments attempts before computing backoff, so the first retry waits 400 ms rather than the documented 200 ms. The loop allows five retry attempts after the initial failure before returning the final error.

Batch loops in `load_all()` call concurrent loaders with the full remaining vector before `split_off(32)`, so when there are 32 or more entries the first iteration may load more than 32 despite the apparent batching intent. This is worth checking for large IAM installations.

Listing is asynchronous and channel based; errors cancel the token, but spawned tasks may continue briefly. Full reload commit uses snapshot matching to avoid overwriting concurrent mutations, but this means a large reload can do all I/O and then drop results if the cache changed.

## Test Signals

Tests cover plaintext JSON acceptance, legacy secret-key and access-secret encryption compatibility, corrupt and short encrypted data failures, plaintext storage when no IAM master key is configured, current master-key encryption round trip, and old-key fallback during rotation. These tests strongly cover crypto compatibility helpers. There is no direct test coverage here for object walking, full `load_all()` cache replacement, storage readiness probing, lazy rewrite ETag behavior, save retry timing, or expired/temp identity deletion against a real or fake `ECStore`.
