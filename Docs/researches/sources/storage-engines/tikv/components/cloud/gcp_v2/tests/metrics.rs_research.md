# sources/storage-engines/tikv/components/cloud/gcp_v2/tests/metrics.rs

## Purpose
Provides integration-style tests for the `gcp_v2` upload path against a local TCP HTTP server. The tests verify that generated-client uploads use resumable upload flow and preserve requested upload options without live GCP services.

## Important APIs, Types, And Functions
- `start_server` launches a Tokio TCP listener, captures raw HTTP requests, and responds to token, resumable-upload initiation, and final upload requests.
- `response_for_target` returns a token response for `/token`, a `Location` header for `uploadType=resumable`, or minimal object JSON.
- `make_cfg` builds `kvproto::brpb::Gcs` test configs.
- `external_account_credentials_blob` creates JSON external-account credentials pointing at the local token endpoint and a subject token file.
- Tests assert resumable upload, predefined ACL, storage class, and zero-length resumable behavior.

## Control Flow
Each test starts the local server, creates a temporary subject token file, injects external-account credentials and custom endpoint into `GcsStorage::from_input`, performs `put`, inspects captured raw request bytes, and sends shutdown. The server reads headers and declared body length before responding so generated client request bodies are captured.

## State And Persistence Behavior
Tests create temporary subject token files and hold captured HTTP requests in `Arc<Mutex<Vec<Vec<u8>>>>`. No repository state is modified.

## Dependencies And Integration Points
Uses `tokio` networking/IO, `tempfile`, `kvproto::brpb::Gcs`, and public `gcp_v2::GcsStorage` plus `cloud::blob::BlobStorage`. It exercises `google-cloud-auth` external-account token exchange through a local endpoint.

## Risks And Edge Cases
The server is intentionally minimal HTTP/1.1 and only handles request patterns required by these tests. Assertions are substring-based, so generated client encoding changes could require updates even if semantics remain valid. Shutdown is best-effort after assertions.

## Test Signals
These tests are the primary active signal that `gcp_v2` does not regress to single-shot upload and preserves storage class/predefined ACL behavior. They also indirectly test external-account credential flow with local token exchange.
