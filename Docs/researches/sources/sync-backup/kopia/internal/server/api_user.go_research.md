# sources/sync-backup/kopia/internal/server/api_user.go

Purpose: returns information about the currently authenticated user.

Important APIs/types/functions: `handleCurrentUser`.

Control flow: reads Basic Auth username from the request and returns it in a serverapi response; wrapper authentication has already validated credentials when configured.

State and persistence behavior: stateless request inspection.

Dependencies and integration points: used by UI session/header code and registered as `/api/v1/current-user`.

Risks and test signals: when authentication is disabled, username may be empty. Tests should cover auth-enabled and auth-disabled modes.
