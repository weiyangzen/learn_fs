# sources/sync-backup/kopia/internal/server/grpc_session.go

Purpose: implements Kopia's repository gRPC session protocol over HTTP/2, including authentication, handshake, concurrent request dispatch, content/manifest operations, retention policy application, notifications, and gRPC routing.

Important APIs/types/functions: `grpcServerState`, `Server.Session`, `authenticateGRPCSession`, `handleInitialSessionHandshake`, `handleSessionRequest`, request handlers for content/manifest/prefetch/retention/notification operations, `accessDeniedResponse`, `errorResponse`, metadata conversion helpers, `RegisterGRPCHandlers`, `makeGRPCServerState`, `GRPCRouterHandler`, and `ShutdownGRPCServer`.

Control flow: `Session` requires a direct repository, authenticates metadata credentials, authorizes the user, performs an initial initialize-session handshake returning repository parameters, then opens a direct write session. Incoming requests are received in a loop, concurrency-limited by a weighted semaphore, processed in goroutines, and responses are serialized through `sendMutex`. Handlers check content or manifest access levels, parse IDs, perform repository operations, paginate manifest search when requested, and map errors to protocol error codes.

State and persistence behavior: content writes, manifest puts/deletes, retention policy application, flushes, and notifications mutate repository state or external notification side effects. Server state includes a lazily created gRPC server, semaphore, and send mutex.

Dependencies and integration points: connects remote repository clients to `repo.DirectRepositoryWriter`, auth/authz, OpenTelemetry trace context, content/manifest/object packages, notification packages, and HTTP router multiplexing.

Risks and test signals: request goroutine errors are reported through a one-slot channel, so later send failures may be dropped; write session lifetime spans the stream; authz label checks are security-critical. Tests should cover metadata auth, handshake ordering, concurrent requests, access denial, pagination, and graceful shutdown behavior.
