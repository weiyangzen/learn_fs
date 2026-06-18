# sources/object-store/garage/src/model/bucket_alias_table.rs

## Purpose
This file defines the global bucket alias table and bucket-name validator. A global alias maps an S3 bucket name to a bucket UUID via an LWW canceling option, allowing aliases to be created, moved to deleted state, replicated, and filtered independently from the bucket records that keep reverse alias hints.

## Important APIs, types, and functions
`BucketAlias` has `name` and `state: Lww<CancelingOption<Uuid>>`. `BucketAlias::new`, `is_deleted`, and `name` construct and inspect alias entries. `Crdt` merge delegates to LWW state. `Entry<EmptyKey, String>` stores all aliases in one partition keyed by alias name. `BucketAliasTable` names the table `bucket_alias` and filters through `DeletedFilter`. `is_valid_bucket_name` enforces Garage's S3 bucket-name rules with optional punycode support, and `INVALID_BUCKET_NAME_MESSAGE` is the client-facing validation text.

## Control flow
Admin and S3 bucket paths use helper methods in `helper/locked.rs` to validate names, read/update `BucketAlias`, and coordinate alias timestamps with reverse maps in `Bucket`. Fast bucket resolution in `helper/bucket.rs` reads the local alias table, while admin paths do quorum reads. The validator checks length, allowed lowercase DNS characters, start/end characters, IP-address shape, `xn--` labels unless configured, and the `-s3alias` suffix.

## State and persistence behavior
The table's initial format is versioned by Garage's migration system. Alias deletion is represented by `CancelingOption(None)` rather than removing the row. LWW timestamps are chosen by locked helper code to be greater than both the alias-table and reverse-map timestamps, giving paired updates deterministic merge behavior.

## Dependencies and integration points
This module depends on `garage_table` CRDT/table traits and `garage_util::data::Uuid`. It integrates with `BucketHelper` resolution, `LockedHelper` alias mutation, bucket creation/deletion admin flows, and the user-facing S3 bucket name constraints.

## Risks and edge cases
The validator intentionally allows dots and rejects IP-looking names, but TLS virtual-host semantics around dotted bucket names still need handling elsewhere. Concurrent alias creation on different API nodes is only partially mitigated by local locking in `LockedHelper`; cross-node races can still create temporary inconsistencies. Punycode validation is controlled by configuration and is stricter for `.xn--` labels than the base AWS rule.

## Test signals
There are no local tests. Useful coverage would include every bucket-name rejection branch, punycode enabled/disabled behavior, LWW alias deletion/recreation, and paired alias/bucket reverse-map repair.
