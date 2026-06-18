# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/lease_schema.py

## Purpose
Defines the lease serialization policy used by immutable and mutable share containers. It separates old cleartext lease formats from newer hashed-secret formats so share code can preserve on-disk compatibility while avoiding storage of future lease renew/cancel secrets in plaintext.

## Important APIs, Types, And Functions
`CleartextLeaseSerializer` wraps `LeaseInfo.to_*_data` and `LeaseInfo.from_*_data` methods and only accepts plaintext `LeaseInfo`. `HashedLeaseSerializer` hashes plaintext `LeaseInfo` secrets with BLAKE2b before serialization and returns `HashedLeaseInfo` on unserialization. `_hash_secret()` is the common 32-byte secret hash function, and `_hash_lease_info()` protects against rehashing by requiring a `LeaseInfo`. The module exports four serializer instances: `v1_immutable`, `v2_immutable`, `v1_mutable`, and `v2_mutable`.

## Control Flow
Callers select a versioned serializer through immutable or mutable schema code. For v1 serialization, the serializer writes the lease exactly as supplied and unserializes directly into `LeaseInfo`. For v2 serialization, plaintext leases are converted to `HashedLeaseInfo`, while already-hashed leases are passed through; deserialization wraps legacy `LeaseInfo.from_*_data` output in `HashedLeaseInfo` so later secret checks hash the presented secret before comparison.

## State And Persistence
The file is stateless except for serializer singletons. Its persistence effect is the byte representation of lease records in share files: v1 stores cleartext renewal and cancellation tokens, while v2 stores BLAKE2b digests. It depends on `HashedLeaseInfo` to preserve the distinction between stored digest bytes and client-provided plaintext secrets.

## Dependencies And Integration Points
Used by `mutable_schema.py` and immutable share schema code to bind container versions to a lease encoding. It depends on `attrs`, PyNaCl BLAKE2b hashing, and `allmydata.storage.lease` types.

## Risks And Test Signals
The main risk is schema mix-up: using a v1 serializer for v2 shares leaks secrets, while double-hashing would make leases impossible to renew or cancel. Tests should cover v1/v2 round trips, `LeaseInfo` versus `HashedLeaseInfo` type rejection, renew/cancel secret matching after reload, and migration behavior for existing cleartext leases.
