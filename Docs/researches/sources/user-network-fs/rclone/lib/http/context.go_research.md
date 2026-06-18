# sources/user-network-fs/rclone/lib/http/context.go

Source read signal: reviewed complete local file (59 lines, sha256 1bff5d07cf16829a).

Purpose: Defines private request context keys and helpers for HTTP auth/user/public URL state.

Important APIs/types/functions: `NewBaseContext`, `IsAuthenticated`, `PublicURL`, `CtxGetAuth`, `CtxGetUser`, and `CtxSetUser`.

Control flow: `NewBaseContext` returns an `http.Server.BaseContext` function that marks Unix-socket listeners or stores the public URL. Auth middleware stores either auth values or usernames; helpers read them from request contexts.

State and persistence behavior: Request-scoped context values only; no persistence.

Dependencies and integration points: Uses `context`, `net`, and `net/http`. Integrated by `server.newInstance` and all auth middleware/handlers.

Risks and test signals: Context keys are private typed ints to avoid collisions. `IsAuthenticated` treats either custom auth value or user as authenticated, so middleware ordering determines semantics.
