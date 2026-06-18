# sources/object-store/garage/src/k2v-client/lib.rs

Purpose: This library implements a typed async client for Garage's K2V HTTP API. It builds signed requests, percent-encodes K2V paths and query parameters, dispatches via Hyper/Rustls, decodes response status/content types, and exposes ergonomic item, range, batch, index, delete, and poll methods.

Important APIs and types: Public API includes `K2vClientConfig`, `K2vClient`, `CausalityToken`, `K2vValue`, `CausalValue`, `PaginatedRange`, `Filter`, `PollRangeFilter`, `PollRangeResult`, `PartitionInfo`, `BatchInsertOp`, `BatchReadOp`, `BatchDeleteOp`, and `Error`. Major methods are `new`, `new_with_client`, `read_item`, `poll_item`, `poll_range`, `insert_item`, `delete_item`, `read_index`, `insert_batch`, `read_batch`, `delete_batch`, `dispatch`, and `build_url`.

Control flow: Client construction creates a native-root HTTPS connector supporting HTTP and HTTPS. Public methods build URLs and JSON or binary bodies for one K2V operation, then call `dispatch`. `dispatch` adds User-Agent and `x-amz-content-sha256`, signs the request using `aws-sigv4` service name `k2v`, sends it with an operation-specific timeout, extracts causality/content-type headers, handles known status codes, parses remote error JSON, and returns a compact `Response`. Decoding methods then map binary/json/tombstone responses into typed values.

State and persistence behavior: The client stores endpoint, region, credentials, bucket, user-agent, and an HTTP client. Remote K2V state is mutated by insert/delete/batch calls; local state is otherwise stateless between requests. Causality tokens are opaque strings used by callers to serialize or branch updates.

Dependencies and integration points: It depends on Hyper, Hyper-Rustls, AWS SigV4, AWS SDK credentials type, percent-encoding, serde, base64, sha2, hex, tokio, and Garage's K2V HTTP protocol conventions. It is used by integration tests and by `k2v-cli`.

Risks: `dispatch` unwraps header values when building the signable request, so non-UTF8 headers would panic. Timeouts are implemented with `tokio::select!` sleep around the request future. `build_url` always emits `key=value` query pairs even for empty query markers. Poll methods depend on server long-poll behavior, which raw tests mark as currently broken. The client treats 404 as `NotFound` without body details.

Test signals: `k2v_client/simple.rs` validates simple insert/read and Unicode key percent-encoding through `read_index` and `read_batch`. Raw K2V tests indirectly validate protocol expectations that this client encodes/decodes.
