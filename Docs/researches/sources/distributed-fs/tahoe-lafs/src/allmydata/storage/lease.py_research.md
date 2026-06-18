# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/lease.py

## Purpose
Defines storage lease interfaces and concrete lease records for immutable and mutable shares, including hashed-secret wrappers for safer persisted lease secrets.

## Important APIs, Types, and Functions
Exports `IMMUTABLE_FORMAT`, `MUTABLE_FORMAT`, `ILeaseInfo`, `LeaseInfo`, `HashedLeaseInfo`, and `_HashedCancelSecret`. `LeaseInfo` serializes/deserializes immutable and mutable lease records, compares renew/cancel secrets, computes age, and creates renewed copies. `HashedLeaseInfo` proxies `ILeaseInfo` while hashing candidate secrets before comparison.

## Control Flow
`LeaseInfo.from_immutable_data()` and `from_mutable_data()` unpack struct records into attrs objects. `to_immutable_data()` and `to_mutable_data()` pack fields for persistence. `renew()` returns an updated immutable attrs copy. `HashedLeaseInfo.is_*_secret()` hashes external candidates and delegates timing-safe comparison; `_HashedCancelSecret` allows in-process lease expiration code to cancel leases when only the hashed cancel secret is known.

## State and Persistence Behavior
Lease records persist owner number, renew secret, cancel secret, expiration time, and for mutable leases nodeid. Version-2 immutable schemas store hashed secrets through lease serializers. `LeaseInfo` objects are frozen; updates create new objects rather than mutating fields.

## Dependencies and Integration Points
Used by immutable and mutable share-file implementations, lease expiration, storage server lease renewal, and HTTP tests. Depends on attrs, Zope interfaces, Twisted `proxyForInterface`, base32 display, and timing-safe comparisons.

## Risks and Edge Cases
`get_grant_renew_time_time()` estimates grant time by subtracting a fixed 31-day interval, so age is approximate. `_HashedCancelSecret` is intentionally an internal bypass and would be dangerous if exposed over a network API. `nodeid` validation is strict 20-byte data for mutable leases.

## Test Signals
`test_storage.py::LeaseInfoTests` covers renew/cancel secret comparison, serialized sizes, and storage share tests cover hashed secret behavior through immutable schemas and lease renewal/cancellation.
