# sources/sync-backup/kopia/internal/server/request_context.go

Purpose: defines the internal request context and server interface abstraction used by API handlers and tests.

Important APIs/types/functions: `serverInterface`, `requestContext`, `muxVar`, and `queryParam`.

Control flow: the server wrapper captures HTTP writer/request, request body, current repository, and server interface. Handler helpers read mux route variables or URL query parameters.

State and persistence behavior: per-request in-memory data only.

Dependencies and integration points: API handlers depend on this instead of concrete `Server`, which simplifies testing and fake server implementations.

Risks and test signals: `serverInterface` is broad, so fake implementations must stay in sync with handler needs. Compile-time use across handlers is the primary guard.
