# sources/object-store/garage/src/api/admin/bucket.rs

Purpose: implements bucket administration: list, lookup, create, update, delete, cleanup incomplete uploads, inspect object versions, grant/revoke key permissions, and manage global/local aliases.

Important handlers/functions: `ListBucketsRequest`, `GetBucketInfoRequest`, `CreateBucketRequest`, `DeleteBucketRequest`, `UpdateBucketRequest`, `CleanupIncompleteUploadsRequest`, `InspectObjectRequest`, `AllowBucketKeyRequest`, `DenyBucketKeyRequest`, `AddBucketAliasRequest`, `RemoveBucketAliasRequest`, `handle_bucket_change_key_perm`, `bucket_info_results`, and `parse_bucket_id`.

Control flow and state: persistent state is spread across bucket table, bucket alias table, key table, object/version tables, object and MPU counter tables, and helper-managed alias/permission links. Create validates requested aliases, inserts a new bucket, then sets aliases and optional key permissions under the locked helper. Delete requires bucket emptiness, revokes key permissions, purges local/global aliases, then writes a bucket delete tombstone. Update mutates website, quota, CORS, and lifecycle CRDT fields. Inspect object reads object versions and joins version blocks to produce version/block metadata.

Dependencies/integration: uses Garage model helpers for locked multi-table changes, bucket/key permission types, S3 object and MPU tables, XML conversion/validation for website/CORS/lifecycle configs, CRDT wrappers, time utilities, and common bucket-name validation.

Risks: alias and permission operations span multiple CRDT tables, so using `locked_helper` is critical. Search by bucket ID prefix can be ambiguous. Delete depends on `is_bucket_empty` correctness. Website disabling rejects stray index/error fields but routing rules behavior follows request shape. Object inspection omits plaintext headers for encrypted variants and reports block metadata only when version rows exist.

Test signals: cover alias validation and conflicts, local alias with key lookup, bucket delete with non-empty buckets, full alias/permission cleanup on delete, website/CORS/lifecycle validation, quota updates, incomplete upload cleanup thresholds, inspect variants for uploading/complete/delete-marker/aborted/inline/first-block versions, and allow/deny partial permission bits.
