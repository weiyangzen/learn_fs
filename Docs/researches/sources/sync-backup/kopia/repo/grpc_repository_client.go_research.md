# sources/sync-backup/kopia/repo/grpc_repository_client.go

Purpose: implements Kopia's remote `Repository` client over the bidirectional gRPC API exposed by `kopia server`. It adapts the local repository interfaces for manifests, contents, objects, retention, notifications, flushes, and write sessions onto `apipb.SessionRequest` and `SessionResponse` messages.

Important APIs/types/functions: `grpcRepositoryClient`, `grpcInnerSession`, `MaxGRPCMessageSize`, `openGRPCAPIRepository`, `newGRPCAPIRepositoryForConnection`, `getOrEstablishInnerSession`, `sendRequest`, `readLoop`, `maybeRetry`, `WriteContent`, `GetContent`, manifest methods, `ContentInfo`, `Flush`, and `baseURLToURI`. `grpcCreds` injects Kopia auth/build metadata as per-RPC credentials.

Control flow: a repository client lazily establishes a streaming session, sends an initialize request, starts `readLoop`, then multiplexes logical requests by request ID through per-request response channels. High-level repository methods choose retryable or non-retryable session access, send one request, interpret the expected response variant, and convert remote error responses into local sentinel errors.

State/persistence behavior: durable state remains server-side; the client stores session state, active request channels, async write verification goroutines, a content cache, recent prefixed reads, object manager state, server parameters, and flush callbacks. `WriteContent` computes the expected content ID locally, sends cloned bytes asynchronously, and `Flush` waits for all asynchronous verification before invoking callbacks and issuing remote flush.

Dependencies/integration: integrates gRPC, TLS/fingerprint trust, OpenTelemetry trace propagation, retry backoff, Kopia content/object/manifest APIs, hashing parameters returned by the server, content cache, compression headers, and remote notification/retention APIs. It supports `https`, `kopia`, and `unix+https` server addresses.

Risks/test signals: the main risks are request-channel leaks, stream break races, losing async write errors until flush, retrying unsafe write operations, local/server hash mismatch, and URL/TLS credential misconfiguration. Tests cover message-size headroom and URL-to-gRPC-target conversion; broader behavior depends on integration coverage around server sessions.
