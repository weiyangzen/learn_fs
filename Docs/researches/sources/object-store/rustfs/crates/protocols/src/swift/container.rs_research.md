# sources/object-store/rustfs/crates/protocols/src/swift/container.rs

## Purpose
This file implements Swift container operations on top of RustFS/S3 bucket primitives. It maps account-scoped Swift container names to tenant-prefixed S3 bucket names, performs container CRUD, lists objects, stores Swift container metadata as bucket tags, manages Swift object versioning configuration, and persists container ACLs through the ACL parser.

## Important APIs, Types, And Functions
- `sanitize_storage_error` logs detailed storage failures while returning a generic `InternalServerError`.
- `swift_metadata_to_s3_tags` and `s3_tags_to_swift_metadata` convert between `X-Container-Meta-*` metadata and `swift-meta-*` S3 bucket tags.
- `ContainerMapperConfig` and `ContainerMapper` implement tenant prefixing. `hash_project_id` uses the first eight bytes of SHA256 as a 16-character hex prefix; `swift_to_s3_bucket`, `s3_to_swift_container`, and `bucket_belongs_to_project` apply or reverse that mapping.
- `bucket_info_to_container` converts `BucketInfo` to the Swift `Container` DTO.
- `list_containers`, `create_container`, `get_container_metadata`, `update_container_metadata`, and `delete_container` implement Swift container CRUD.
- `list_objects` implements Swift container object listing by calling `list_objects_v2`.
- `enable_versioning`, `disable_versioning`, and `get_versions_location` manage the `swift-versions-location` bucket tag.
- `set_container_acl`, `get_container_acl`, and `delete_container_acl` store and retrieve ACL header values in `swift-acl-read` and `swift-acl-write` bucket tags.

## Control Flow
Most public operations first call `validate_account_access` to extract the Keystone project id, validate the Swift container name, instantiate the default tenant-prefix mapper, and resolve the global object store handle. The mapped bucket name is then used for storage API calls.

`list_containers` lists all buckets, filters by the project hash prefix, and converts matching buckets to Swift containers. `create_container` checks existence and returns `Ok(false)` for an existing bucket so the handler can return Swift `202 Accepted`; otherwise it creates the bucket and returns `Ok(true)`. `delete_container` verifies existence and then deletes with `force: false`, mapping non-empty bucket errors to Swift conflict.

`get_container_metadata` verifies the bucket, then loads bucket metadata tags and extracts only `swift-meta-*` tags into `custom_metadata`; object count and bytes used are currently placeholders. `update_container_metadata` verifies existence, loads current bucket metadata, removes old `swift-meta-*` tags while preserving other tags, appends converted Swift metadata tags, serializes tags to XML when non-empty, and writes the bucket metadata back.

`list_objects` checks bucket existence, prepares max keys, prefix, marker, and delimiter arguments, calls `list_objects_v2`, and maps returned object metadata into Swift object DTOs with name, ETag, size, content type, and RFC3339 modification time.

Versioning and ACL operations follow the same tag-editing pattern. Versioning requires the archive container to exist and differ from the source container before writing `swift-versions-location`. ACL setting validates header strings through `ContainerAcl` before replacing the ACL tag pair. ACL retrieval loads tags and reparses values into a `ContainerAcl`.

## State And Persistence Behavior
Container existence maps directly to S3 bucket existence. Tenant isolation is encoded in bucket names by a deterministic project hash prefix. Swift custom metadata, versioning configuration, and ACLs are persisted as bucket tags in RustFS bucket metadata; tag XML and parsed tag config are updated together with a new `tagging_config_updated_at` timestamp.

Tag updates are namespace-specific replacements. Metadata updates remove only `swift-meta-*` tags. Versioning updates remove only `swift-versions-location`. ACL updates remove only `swift-acl-read` and `swift-acl-write`. Other tags are preserved across all of these operations.

Object listing is read-only. Object counts and byte totals in container metadata/listing are currently not persisted or computed in this module and are returned as zero.

## Dependencies And Integration Points
This module depends on `account::validate_account_access`, Swift DTOs from `types`, `rustfs_ecstore::resolve_object_store_handle`, bucket/list storage traits, `rustfs_storage_api` bucket option types, `s3s::dto::{Tag, Tagging}`, SHA256, `quick_xml`, `time`, and `tracing`.

It is the central Swift container service used by higher-level HTTP handlers, CORS loading (`cors.rs`), bulk extract validation (`bulk.rs`), object-versioning logic in `object.rs`, and ACL enforcement/retrieval via `acl.rs`.

## Risks And Edge Cases
- The default mapper always enables tenant prefixing, but disabling prefixing makes `bucket_belongs_to_project` return true for all buckets, weakening tenant isolation.
- Container names are validated only for non-empty, length <= 256, and no slash. S3 bucket naming restrictions are stricter, so some Swift-valid names may fail storage creation later.
- Error mapping often checks substrings such as `"not found"` or `"NoSuchBucket"`, which can be brittle across storage error formatting.
- Metadata, versioning, and ACL updates use read-modify-write on bucket metadata with no explicit concurrency control in this file; concurrent updates to different tag namespaces can race and lose changes.
- `get_versions_location` returns `Ok(None)` for any metadata load error, potentially hiding storage failures as "versioning disabled".
- Object count and byte usage are placeholders, so Swift clients that depend on accurate container stats receive zeros.
- ACL default semantics rely on `acl.rs` and caller context; this module stores/retrieves ACLs but does not enforce them in container operations.

## Test Signals
The test module covers tenant hash mapping, reverse mapping, project ownership checks, bucket-to-container conversion, container-name validation, collision prevention for ambiguous tenant/container separator cases, hash determinism and S3-compatible characters, metadata-to-tag conversion, tag-to-metadata extraction, case normalization, round trips, tag preservation/removal behavior, and versioning tag format/update/removal helpers. There are no async integration tests for real bucket creation/deletion, metadata persistence through `metadata_sys`, object listing, ACL persistence, or concurrent tag updates.
