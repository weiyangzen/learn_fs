# sources/object-store/rustfs/crates/ecstore/src/bucket/bucket_target_sys.rs

Purpose: manages remote bucket targets for replication or related services, including target validation, cached AWS S3 clients, endpoint health metadata, bandwidth limit updates, and remote object operations with internal replication headers.

Important APIs and types: global `BucketTargetSys` stores ARN-to-client map, bucket target map, endpoint health, health-check HTTP client, and ARN error state behind async locks. `TargetClient` wraps an AWS S3 client and implements `bucket_exists`, `get_bucket_versioning`, `head_object`, `put_object`, multipart upload/part/complete, and `remove_object`. Option structs model remove, put, advanced replication, and part headers. `BucketTargetError` and `S3ClientError` normalize errors.

Control flow: target setup validates type, credentials placeholder, bucket existence, and versioning requirements for replication. `update_all_targets` removes old targets, clears bandwidth throttles, builds new clients, installs ARN mappings, and applies bandwidth limits. `get_remote_target_client` reloads target config when cached client is missing and refresh cooldown allows. Header builders inject source version, etag, mtime, delete marker, governance, and replication flags through AWS SDK `customize().map_request`.

State and persistence: runtime maps are in memory. Durable source is bucket metadata/config loaded through metadata systems. TLS trust can be loaded from configured certificate files. Bandwidth state is delegated to the global bucket monitor.

Dependencies and integration points: AWS SDK S3, smithy HTTP/TLS, RustFS bucket metadata, replication config, versioning system, target ARN types, global monitor, rustfs HTTP header constants, and rustls cert config.

Risks: `check_endpoint_health` currently always returns true, so health status is optimistic. `validate_target_credentials` is a stub. Custom header insertion unwraps header pairs and string conversion in several paths. `LastMinuteLatency::add` retention uses a fixed start time rather than per-sample timestamps. A put header condition appears inverted for `source_etag` insertion. Target maps can diverge from persisted metadata until refreshed.

Test signals: unit tests verify remove-object internal version headers and delete-marker purge header behavior. Most target validation/client behavior needs integration tests with real S3-compatible remotes.
