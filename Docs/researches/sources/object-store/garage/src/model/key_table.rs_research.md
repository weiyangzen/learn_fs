# sources/object-store/garage/src/model/key_table.rs

## Purpose
This file defines the replicated S3 access-key metadata table. It stores key IDs, secrets, names, optional expiration, create-bucket privileges, bucket permissions, and key-local bucket aliases.

## Important APIs, types, and functions
`Key` stores `key_id` and `crdt::Deletable<KeyParams>`. `KeyParams` includes creation time, immutable `secret_key`, LWW `name`, LWW optional `ExpirationTime`, LWW `allow_create_bucket`, CRDT map of authorized buckets, and LWW map of local aliases. `Key::new` generates Garage-style key IDs and random secrets. `Key::import` validates user-provided IDs/secrets. `delete`, `is_deleted`, `params`, `params_mut`, `bucket_permissions`, `allow_read`, `allow_write`, `allow_owner`, and `KeyParams::is_expired` are core operations. `KeyTable` uses `KeyFilter` for deleted and prefix/name matching.

## Control flow
New keys are created with ID prefix `GK`, 12 random bytes hex-encoded, and 32 random bytes hex-encoded as secret. Imported keys enforce minimum ID/secret lengths and ASCII character constraints. Permission checks read the CRDT map and default to no permissions. Search filters match non-deleted key prefixes or exact lowercased names.

## State and persistence behavior
Current format `G2key` migrates from v08 by adding optional creation timestamp and expiration. Deletes are tombstones via `Deletable`. Secret keys are stored in plaintext metadata, so metadata DB access is sensitive. Local aliases and authorized bucket maps are denormalized with bucket table state by `LockedHelper`.

## Dependencies and integration points
It depends on Garage CRDT/time/data/table modules and `BucketKeyPerm`. `Garage::new` creates a fully replicated `key_table`; S3 auth uses keys; admin APIs and `LockedHelper` mutate keys; bucket resolution checks local aliases.

## Risks and edge cases
Plaintext secret persistence requires protecting metadata snapshots/backups. `Key::import` accepts any graphic ASCII secret of length >=16, not necessarily high entropy. Concurrent permission/local-alias edits rely on timestamps in nested CRDTs. Deleted keys may retain historical state in tombstones until compaction/migration.

## Test signals
No direct tests in this file. Useful coverage includes generated/imported key validation, expiration checks, filter matching, permission defaults, v08 migration, and paired mutation with bucket table.
