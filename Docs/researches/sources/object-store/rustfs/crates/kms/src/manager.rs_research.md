# sources/object-store/rustfs/crates/kms/src/manager.rs

## Purpose
Coordinates KMS backend operations and optional key metadata caching behind a cloneable manager used by object encryption services.

## Important APIs, Types, And Functions
`KmsManager` stores an `Arc<dyn KmsBackend>`, `Arc<RwLock<KmsCache>>`, and `KmsConfig`. Public async methods delegate create/encrypt/decrypt/generate data key/describe/list/delete/cancel deletion/health check. It also exposes `get_default_key_id`, `cache_stats`, and `clear_cache`.

## Control Flow
Create, describe, delete, and cancel deletion update or consult the metadata cache when enabled. Encrypt, decrypt, generate data key, list keys, and health check delegate directly to the backend. `describe_key` checks cache first, then backfills cache from the backend response.

## State And Persistence
The manager's only state is in-memory metadata cache. It intentionally does not cache generated DEKs or ciphertext blobs; generated data keys are delegated every time to preserve per-object context binding.

## Dependencies And Integration
Depends on the `KmsBackend` trait, `KmsCache`, config, request/response types, and Tokio `RwLock`. `service.rs` wraps it for object-level SSE behavior, and `service_manager.rs` constructs it for each service version.

## Risks And Edge Cases
Cache TTL from `CacheConfig` is not passed into `KmsCache::new` here, only `max_keys`; if `KmsCache` supports TTL separately, that config may be ignored. Cache invalidation is limited to delete/cancel/create/describe paths and depends on backend responses being authoritative.

## Test Signals
Tests cover local backend create key, generate data key, describe, cache stats, health check, and a regression asserting generated data key ciphertext differs across different object contexts and decrypts only with its own context.
