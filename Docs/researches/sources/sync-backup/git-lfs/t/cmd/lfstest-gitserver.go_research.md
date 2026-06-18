# sources/sync-backup/git-lfs/t/cmd/lfstest-gitserver.go

Purpose: comprehensive in-process HTTP/HTTPS Git and Git LFS test server used by integration tests.

Important APIs/types/functions: server bootstrap in `main`; LFS structs `lfsObject`, `lfsLink`, `lfsError`; handlers `lfsHandler`, `lfsBatchHandler`, `storageHandler`, `verifyHandler`, `gitHandler`, `locksHandler`, `redirect307Handler`, `limitsHandler`; lock structs `Lock`, `LockRequest`, `LockList`, `VerifiableLockList`; storage type `lfsStorage`; auth helpers `extractAuth`, `skipIfBadAuth`, `missingRequiredCreds`; TLS helpers `generateCARootCertificates`, `generateClientCertificates`, `CertTemplate`, and `CreateCert`.

Control flow: starts HTTP, TLS, and client-cert TLS `httptest` servers on one mux, writes URL/cert/key paths to state files, and blocks until `/shutdown`. Requests under `/info/lfs` go to LFS batch/lock handlers after accept/content-type/auth checks. Other Git requests are forwarded to `git http-backend`. Storage endpoints implement PUT/GET/HEAD/PATCH, including retries, rate limits, range resume, gzip/zstd encoding, TUS uploads, corruption, redirects, and status injection triggered by magic object contents.

State/persistence behavior: in-memory maps store complete/incomplete LFS objects, locks, retry counters, rate-limit tokens, expired-action state, and verify counts. State files expose URLs/certs to shell tests; Git repository data lives under `LFSTEST_DIR` and is served through `git http-backend`.

Dependencies/integration: central fixture for batch API, storage API, locks API, auth, netrc, custom transfers, chunked/TUS transfers, redirects, retry logic, hash-algorithm handling, TLS/client-cert tests, and Git smart HTTP.

Risks: large mutable global state means tests must isolate repo names/OIDs. Some branches call `log.Fatal`, killing the whole server. Lock pagination appears to cap size with `min(len(locks), 3)` instead of requested limit, so behavior is fixture-specific.

Test signals: integration tests observe HTTP status codes, LFS JSON bodies, stored object data, locks, retry behavior, logs, and generated cert/url files.
