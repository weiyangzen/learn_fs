# sources/object-store/rustfs/crates/protocols/src/swift/account.rs

## Purpose
This file implements Swift account-level validation and account metadata helpers for the Swift protocol layer. Its main job is tenant isolation: it checks that a Swift account path such as `AUTH_<project_id>` matches the Keystone project id embedded in authenticated credentials. It also stores account-level Swift metadata, especially TempURL keys, in a dedicated hidden S3 bucket represented by RustFS bucket metadata tags.

## Important APIs, Types, And Functions
- `validate_account_access(account, credentials) -> SwiftResult<String>` strips the `AUTH_` prefix, extracts `keystone_project_id` from credential claims, and returns the project id only when both match.
- `is_admin_user(credentials) -> bool` checks `keystone_roles` claims for `admin` or `reseller_admin`.
- `get_account_metadata_bucket_name(account) -> String` hashes the account with SHA256 and builds `swift-account-<first16hex>`.
- `get_account_metadata(account, credentials)` loads bucket metadata and returns tags whose keys start with `swift-account-meta-`.
- `update_account_metadata(account, metadata, credentials)` creates the metadata bucket if missing, replaces only `swift-account-meta-*` tags, preserves unrelated tags, serializes `Tagging` XML, and writes bucket metadata back through `metadata_sys`.
- `get_tempurl_key(account, credentials)` returns the `temp-url-key` account metadata value when present.

## Control Flow
Account access validation is synchronous and claim-driven. Missing `AUTH_` prefix returns `BadRequest`; missing Keystone project id returns `Unauthorized`; project mismatch returns `Forbidden`; success returns the project id string used by container mapping.

Metadata reads compute the hashed metadata bucket name and call `rustfs_ecstore::bucket::metadata_sys::get`. Any error is treated as absent metadata and returns an empty map. When metadata exists, only tags with the account metadata prefix are copied into the result with the prefix stripped.

Metadata writes resolve the global object store handle, create the metadata bucket if `metadata_sys::get` does not find it, reload bucket metadata, remove old Swift account metadata tags, append new tags, and persist the updated metadata. An empty resulting tag set clears both parsed and XML tagging fields; a non-empty set is serialized with `quick_xml`.

## State And Persistence Behavior
Persistent account state is stored in a synthetic bucket named by a deterministic hash of the account id. Account metadata is encoded as S3 bucket tags using the `swift-account-meta-` namespace. Updates are replace-all for Swift account metadata keys, not patch-by-key: every old prefixed tag is removed before the supplied map is written. Non-Swift bucket tags are deliberately preserved.

The metadata bucket may be created lazily. The `credentials` argument is currently unused in metadata functions, so authorization and tenant validation must happen before these helpers are called.

## Dependencies And Integration Points
The module depends on `rustfs_credentials::Credentials` for Keystone claims, `rustfs_ecstore::resolve_object_store_handle` and `metadata_sys` for storage access, `rustfs_storage_api::MakeBucketOptions` for lazy bucket creation, `s3s::dto::{Tag, Tagging}` for tag representation, SHA256/hex for deterministic bucket naming, `quick_xml` for tag serialization, and the local `SwiftError`/`SwiftResult` model.

`validate_account_access` is called by container operations to derive the project id used for tenant bucket prefixes. `get_tempurl_key` is a likely integration point for Swift TempURL request authentication.

## Risks And Edge Cases
- `get_account_metadata` treats every metadata load error as "no metadata", which can hide storage failures from TempURL or account metadata callers.
- The account metadata bucket name uses only 16 hex characters of SHA256. Collision risk is low but nonzero by construction.
- Metadata writes do not validate tag count, key length, or value length against any S3 tag limits in this file.
- Credentials are ignored by metadata read/write helpers, so callers must validate account access and authorization externally.
- Lazy bucket creation uses default options and may expose account metadata buckets to normal bucket listings unless other layers hide the `swift-account-` naming convention.

## Test Signals
Unit tests cover successful account validation, mismatched account/project, invalid account format, missing project id, admin and reseller-admin role detection, non-admin defaults, and deterministic hashed account metadata bucket naming. There are no async storage tests for metadata read/write persistence, tag preservation, XML serialization, or error behavior.
