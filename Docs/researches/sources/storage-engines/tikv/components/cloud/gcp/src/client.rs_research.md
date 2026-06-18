# sources/storage-engines/tikv/components/cloud/gcp/src/client.rs

## Purpose
Provides the legacy GCP HTTP/auth client used by GCS and KMS. It builds a Hyper HTTPS client, loads service-account/authorized-user/default credentials, injects OAuth authorization headers, and maps request failures into retry-aware errors.

## Important APIs, Types, And Functions
- `GcpClient` holds an optional `TokenProviderWrapper` and a Hyper client.
- `with_svc_info`, `with_default_provider`, and `load_from` construct clients from embedded service account info, default provider lookup, or credential files.
- `set_auth` obtains or exchanges OAuth tokens and inserts the `Authorization` header.
- `make_request` applies auth when configured, sends the request, and turns non-success status into `RequestError`.
- `CredentialType` parses JSON `type` for `service_account` or `authorized_user`.
- `RequestError` models Hyper, OAuth, GCS, and invalid-endpoint failures and implements `RetryError`.

## Control Flow
Credential loading reads a path when provided, deserializes enough JSON to determine credential type, then constructs the appropriate tame OAuth provider. Requests call `set_auth` if a provider exists. `set_auth` may return an existing token or perform an HTTP token request with the same Hyper client, parse the response, and insert auth before sending the original request.

## State And Persistence Behavior
The client stores token-provider state in an `Arc<TokenProviderWrapper>`; token caching is owned by tame-oauth internals. It reads credential files from disk but writes no local state.

## Dependencies And Integration Points
Used by `gcs.rs` for GCS object requests and by `kms.rs` for Cloud KMS REST calls. It depends on `hyper`, `hyper_tls`, `http`, `tame_oauth`, `tame_gcs`, `serde`, and TiKV `RetryError`.

## Risks And Edge Cases
Default-provider construction fails if no environment/default credentials are usable. Error mapping turns some Hyper failures into `InvalidInput` `io::Error`s while retry classification still marks connect/closed/incomplete/body-aborted as retryable. HTTP 401/403 become permission denied and non-retryable; 408/429/5xx OAuth status codes are retryable.

## Test Signals
No local tests. Behavior is indirectly exercised through legacy GCS/KMS tests and integration tests using credential files or mocked endpoints.
