# sources/storage-engines/tikv/components/cloud/gcp/src/gcs.rs

## Purpose
Implements the legacy GCS blob storage backend behind `BlobStorage`, `IterableStorage`, and `DeletableStorage` using `tame-gcs` request builders and the local `GcpClient`.

## Important APIs, Types, And Functions
- `Config` stores `BucketConf`, parsed predefined ACL, storage class, and optional service-account info from `credentials_blob`.
- `Config::from_input` validates bucket, endpoint, prefix, storage class, ACL, and service-account JSON.
- `GcsStorage` owns `Config` and `GcpClient`.
- `maybe_prefix_key` and `strip_prefix_if_needed` implement object key namespace mapping.
- `make_request` rewrites hard-coded `www.googleapis.com` URLs to a custom endpoint if configured.
- `put` handles zero-length objects with `insert_simple` and non-empty objects with buffered `insert_multipart`.
- `get_range`, `get`, `get_part`, `GcsPrefixIter`, and `delete` implement reads, listing, and deletion.

## Control Flow
Construction converts kvproto input into typed options and creates a GCP client from service-account info when present. Put prefixes the name, builds an `ObjectId`, and either inserts an empty object or reads the whole stream into a `Vec<u8>` before multipart upload. Reads construct a download request, optionally set `Range`, send it, and flatten the Hyper body into an async reader. Listing uses `try_unfold` over page tokens until GCS returns no page token.

## State And Persistence Behavior
Persistent data is in GCS objects. Local state is immutable config and client/auth state. Prefixes are stored as configuration and not persisted separately. Uploads are not resumable at this layer; retries reuse buffered data.

## Dependencies And Integration Points
Depends on shared `cloud::blob` traits and metrics, `kvproto::brpb::Gcs`, `tame_gcs`, `tame_oauth`, Hyper, futures, and crate `utils::retry`. It integrates with TiKV backup/restore storage selection through `GcsStorage`.

## Risks And Edge Cases
Non-empty uploads buffer and clone entire objects. `get_part` computes `off + len - 1`, so `len == 0` underflows. Endpoint rewriting only handles URLs starting with `https://www.googleapis.com`. List entries with missing object names become empty keys. Stream body errors are `Interrupted`, so retries must happen at the consuming layer.

## Test Signals
Unit tests cover custom endpoint rewriting, storage-class parsing, predefined-ACL parsing, and backend URL formatting. There are no active tests for upload retry memory behavior, delete/list pagination, partial read underflow, or credential parsing failures.
