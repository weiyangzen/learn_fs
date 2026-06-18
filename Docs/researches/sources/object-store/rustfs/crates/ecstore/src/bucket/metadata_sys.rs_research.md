# sources/object-store/rustfs/crates/ecstore/src/bucket/metadata_sys.rs

Purpose: Provides the global bucket metadata cache and public async accessors for bucket-level configuration. It initializes metadata for existing buckets, reloads missing entries from disk, updates/deletes config blobs, and exposes typed getters used by policy, quota, lifecycle, object lock, replication, and API handlers.

Important APIs and types: `GLOBAL_BucketMetadataSys` is a `OnceLock<Arc<RwLock<BucketMetadataSys>>>`. Top-level functions include `init_bucket_metadata_sys`, `get`, `update`, `delete`, `created_at`, and many typed getters. `BucketMetadataSys` owns `metadata_map: RwLock<HashMap<String, Arc<BucketMetadata>>>`, an `Arc<ECStore>`, and an `initialized` flag.

Control flow and state: Initialization batches bucket loads by `GLOBAL_Endpoints.es_count() * 10`, heals buckets, loads metadata, caches it, and updates `BucketTargetSys`. `get_config` returns cached metadata or loads from disk, inserting the result; if initialized and load fails, it maps the condition to `errBucketMetadataNotInitialized`. Updates call `load_bucket_metadata_parse`, mutate raw bytes through `BucketMetadata::update_config`, save the full metadata record, then replace the cache entry. Deletes route through `update_and_parse` with empty bytes; lifecycle delete has a placeholder parse hook.

Dependencies and integration: Integrates with global endpoint topology, erasure-mode checks, object-store healing, metadata persistence, bucket target system, config deserialization, and S3 DTO types. Public getters are the narrow interface consumed by policy, object lock, lifecycle, notification, quota, replication, website, CORS, and encryption paths.

Risks: The global `OnceLock` cannot be reinitialized in-process, which complicates tests and multi-store scenarios. `update_and_parse` obtains the global object store rather than using `self.api`, so cache instances are not fully self-contained. Failed parse warnings can still allow saved raw bytes. Several TODOs mark missing distributed refresh and notifier/target reload behavior.

Test signals: No local unit tests in this file. Behavior is indirectly covered by metadata codec tests and downstream modules that use the typed getters.
