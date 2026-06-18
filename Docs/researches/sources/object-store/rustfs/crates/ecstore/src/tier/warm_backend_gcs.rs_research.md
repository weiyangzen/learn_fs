# sources/object-store/rustfs/crates/ecstore/src/tier/warm_backend_gcs.rs

## Purpose

Google Cloud Storage warm-tier adapter using `google_cloud_storage`.

## Important APIs and Types

`WarmBackendGCS` stores `Arc<Storage>`, bucket, prefix, and storage class. `new` builds credentials/client from `TierGCS`; `get_dest` joins prefix/object; trait methods implement put/get/remove/in-use.

## Control Flow

Constructor validates creds and bucket, parses credential JSON as authorized-user credentials, and builds a storage client. Put reads the full reader into memory, writes buffered object bytes, and returns generation as version id. Get streams chunks into memory and returns a cursor. Remove is currently no-op; `in_use` currently returns false.

## State and Persistence Behavior

Puts persist remote GCS objects. No local durable state. Remove/in-use behavior currently does not reflect remote state, risking retained objects and false-empty checks.

## Dependencies and Integration Points

Depends on Google auth/storage crates, `bytes`, `TierGCS`, `WarmBackend`, and transition reader abstractions.

## Risks and Edge Cases

Ignores metadata, range, version/generation on read/remove, storage class, and real non-empty checks. Full-object buffering can be expensive. Credential parsing may not support all GCS JSON types.

## Test Signals

No tests; high-priority gaps are delete, generation/range reads, metadata, in-use listing, credential formats, and large object behavior.
