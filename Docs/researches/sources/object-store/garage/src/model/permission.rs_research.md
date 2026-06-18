# sources/object-store/garage/src/model/permission.rs

## Purpose
This file defines CRDT-compatible permission and expiration primitives shared by access keys, buckets, and admin tokens.

## Important APIs, types, and functions
`BucketKeyPerm` stores a timestamp and read/write/owner booleans. Constants `NO_PERMISSIONS` and `ALL_PERMISSIONS` seed common permission states. `is_any` checks whether any permission is granted. Its `Crdt` merge chooses the greater timestamp; if timestamps tie but values differ, it logs a warning and merges to the most restrictive permission set. `ExpirationTime(pub u64)` merges to the earliest timestamp.

## Control flow
Permission mutation code in `LockedHelper` advances timestamps before writing paired bucket/key maps. CRDT merges resolve concurrent permission states using the timestamp. Expiration checks in key/token params compare current time to `ExpirationTime.0`.

## State and persistence behavior
These types are serialized into bucket, key, and admin token table records. Permission timestamps are logical clocks, not just wall-clock timestamps. Expiration times use millisecond timestamps.

## Dependencies and integration points
It depends on `serde` and `garage_util::crdt`. `BucketKeyPerm` is embedded in `BucketParams.authorized_keys` and `KeyParams.authorized_buckets`; `ExpirationTime` is embedded in key and admin token params.

## Risks and edge cases
Equal timestamp conflicts intentionally reduce permissions, which is safe but may surprise admins after concurrent writes. Callers must use logical-clock helpers to avoid equal timestamps for intended updates. Expiration merge chooses the minimum, so concurrent changes converge toward earlier expiration.

## Test signals
No direct tests. Useful tests should cover permission timestamp ordering, equal-timestamp conflict restriction, expiration minimum merge, and paired bucket/key permission updates.
