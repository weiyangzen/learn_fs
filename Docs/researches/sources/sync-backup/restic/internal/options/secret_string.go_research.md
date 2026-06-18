## sources/sync-backup/restic/internal/options/secret_string.go

Purpose: wrapper type for strings that must be hidden in formatting/logging while still retrievable by trusted code.

Important APIs/types: `SecretString` holds a `*string`. `NewSecretString` stores a pointer to a copy of the provided string. `String` returns `**redacted**` for non-empty secrets and empty string otherwise. `GoString` wraps the redacted string in quotes for `%#v`. `Unwrap` returns the underlying secret or empty string for a nil/default value.

Control flow and state: the wrapper is immutable unless the internal pointer target is somehow modified through package internals. Default zero values are safe and render as empty.

Dependencies and integration points: used for option/config values that may appear in struct formatting. It relies on Go formatting calling `String`/`GoString`.

Risks and test signals: `Unwrap` exposes the secret by design; callers must avoid logging it. Empty secrets are not redacted, which is useful for defaults but can reveal the difference between empty and non-empty values. Tests verify formatting and struct formatting do not leak the secret.
