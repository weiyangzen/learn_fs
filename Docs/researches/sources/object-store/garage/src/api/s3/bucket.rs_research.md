# sources/object-store/garage/src/api/s3/bucket.rs

## Purpose
Implements bucket-level S3 operations that are directly backed by Garage bucket/key metadata: bucket location, versioning stub, bucket ACL projection, list-buckets, create-bucket, and delete-bucket. It translates Garage's bucket alias and key permission model into AWS-shaped XML responses and mutates bucket/key alias tables through the locked helper layer.

## Important APIs, Types, And Functions
`handle_get_bucket_location` serializes the configured S3 region as `LocationConstraint`. `handle_get_bucket_versioning` returns an empty versioning configuration, signalling that full S3 versioning is not exposed here. `handle_get_bucket_acl` maps the current key's `BucketKeyPerm` into S3 grants using `create_grantee`. `handle_list_buckets` enumerates authorized bucket IDs from the key state, resolves active global aliases and key-local aliases, and returns `ListAllMyBucketsResult`. `handle_create_bucket` parses optional location XML, validates region and bucket name, then creates a `Bucket`, grants full permissions to the creator, and sets a local alias. `handle_delete_bucket` decides whether a delete removes only an alias or the bucket record itself. `parse_create_bucket_xml` is the XML helper covered by unit tests.

## Control Flow
Create bucket consumes the request body, rejects mismatched `LocationConstraint`, then takes `garage.locked_helper()` so alias and permission updates are serialized. It refetches the API key while locked, resolves any existing bucket name, returns AWS-compatible duplicate-bucket errors, validates creation permission and bucket naming, and writes bucket/key/alias state. Delete bucket also uses the locked helper. It detects whether the target name is a key-local alias, checks whether any other global or local aliases remain, and only performs true bucket deletion if this was the final alias and `is_bucket_empty` succeeds.

## State And Persistence
Persistent state lives in `bucket_table`, `bucket_alias_table`, and key-local alias/permission CRDT fields. Bucket creation inserts a new `Bucket`, writes key permissions with `BucketKeyPerm::ALL_PERMISSIONS`, and stores the bucket name as a local alias for the creator. Full deletion purges the alias, removes all authorized key permissions, and inserts a deleted bucket tombstone. Alias-only deletion updates either local or global alias state without deleting the underlying bucket.

## Dependencies And Integration Points
This module depends on `garage_model` bucket/key tables, `garage_table::util::EmptyKey`, CRDT `Deletable`, helper error mapping, and `crate::xml` S3 response types. It is called by the S3 request dispatcher after `ReqCtx` has resolved bucket, key, permissions, and bucket parameters.

## Risks And Test Signals
The main correctness risks are alias semantics, stale key permissions, and delete races around bucket emptiness. The locked helper lowers alias/permission race risk, but bucket emptiness is only as reliable as helper semantics. `parse_create_bucket_xml` has focused tests for empty, valid, region-bearing, and malformed XML. There are no direct tests here for alias deletion or list-bucket authorization filtering.
