# sources/storage-engines/tikv/components/cloud/gcp_v2/src/lib.rs

## Purpose
Implements the v2 GCS blob storage backend using generated `google-cloud-storage` clients. It preserves TiKV's `BlobStorage`, `IterableStorage`, and `DeletableStorage` contracts while using resumable uploads, generated data/control clients, deferred credentials, custom endpoints, and retry-aware error mapping.

## Important APIs, Types, And Functions
- `GcsApiError` wraps `google_cloud_storage::Error`, maps HTTP/gRPC/transport statuses to `io::ErrorKind`, and implements retry classification.
- `PutResourceSource` adapts TiKV `PutResource` into `StreamingSource` with exact size hints and 256 KiB read chunks.
- `Config` stores bucket, normalized prefix, URL prefix, endpoint, storage class, and predefined ACL.
- `GcsStorage` wraps an `Arc<GcsStorageInner>` so cloned storage shares lazily initialized clients.
- `GcsStorageInner` lazily creates separate `Storage` data and `StorageControl` control clients.
- `from_input` validates rustls provider, kvproto input, storage class/ACL, credential JSON, and stores credential modes.
- `put_with_client`, `get_range`, `iter_prefix`, and `delete` implement writes, reads, listing, and deletion.

## Control Flow
Construction is synchronous and avoids building Google credentials to prevent `tokio::spawn` panics on non-Tokio backup worker threads. First data/control operation initializes the appropriate client in async context. `put` computes full object path and bucket resource name, gets the data client, then uses `put_with_client`; that function widens reader lifetime with a documented `unsafe` block and awaits buffered upload before returning. Reads retry initial `read_object` send, then yield response chunks. Listing loops on `next_page_token`; delete retries generated control API calls.

## State And Persistence Behavior
Persistent state is GCS object data. Local state is config, optional credential JSON, endpoints, and cached generated clients. Prefix normalization trims trailing slashes for object paths while preserving `url_prefix` for backend URL display.

## Dependencies And Integration Points
Depends on `cloud::blob` contracts/metrics, `kvproto::brpb::Gcs`, `google-cloud-storage`, `google-cloud-gax`, local credential helpers, `tokio`, `futures`, `async-stream`, `bytes`, `url`, and TiKV logging/retry utilities. It re-exports `GcpKms`.

## Risks And Edge Cases
`put_with_client` uses `unsafe transmute` and depends on `send_buffered()` not detaching payloads in `google-cloud-storage 1.0.0`. Forced resumable upload changes request shape/latency even for zero-length objects. Read retries do not cover mid-stream errors after bytes are yielded. Bucket resource conversion trusts strings starting with `projects/`.

## Test Signals
Unit tests cover gRPC error mapping, prefix trimming, custom endpoint credential mode, URL formatting, and upload metric emission for non-empty and zero-length uploads through a stub client. Integration tests verify resumable upload, storage class, ACL, and zero-length behavior.
