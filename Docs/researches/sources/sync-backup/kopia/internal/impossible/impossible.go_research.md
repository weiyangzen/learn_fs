# sources/sync-backup/kopia/internal/impossible/impossible.go

Purpose: provides a tiny helper for code paths that consider an error impossible and prefer panic over repetitive error handling.

Important APIs/types/functions: `PanicOnError`.

Control flow: the function checks `err != nil` and panics with the error value if present; nil is a no-op.

State/persistence behavior: no state is stored or persisted. Its effect is immediate control-flow termination through panic.

Dependencies/integration: no external dependencies. Intended for internal use where an API returns an error for interface reasons but the caller believes failure cannot occur.

Risks/test signals: misuse can convert recoverable runtime errors into panics. Callers should reserve it for truly impossible branches or test helpers.
