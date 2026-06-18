<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/typed-errors.go -->
# sources/object-store/minio-mc/cmd/typed-errors.go

Purpose: defines typed error constructors used throughout the command package so callers can distinguish common validation and operation failures while presenting consistent messages.

Important APIs/types/functions: error marker types such as `dummyErr`, `invalidArgumentErr`, `unableToGuessErr`, `invalidAliasedURLErr`, `invalidAliasErr`, `invalidURLErr`, copy/move target/source errors, and SSE-specific errors; constructor variables like `errDummy`, `errInvalidArgument`, `errInvalidAlias`, `errRequiresRecursive`, `errSSEKeyMissing`, and `errSSEClientKeyFormat`.

Control flow: each constructor builds a message, wraps it in `probe.NewError`, and often calls `.Untrace()` to suppress stack traces for user-facing validation errors. Some constructors format dynamic values such as URLs, aliases, diff types, API signatures, or overlapping SSE prefixes.

State and persistence: no state; constructors allocate probe errors.

Dependencies and integration points: heavily used across CLI validation paths, copy/move/encryption code, and tests that inspect error JSON. Depends on `probe` and shared package constants like `validAPIs`.

Risks and test signals: misspellings and message text changes can affect scripted users and tests. Tests should validate error types/messages for CLI JSON output, trace suppression, and sentinel wrapping where callers use type assertions.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/typed-errors.go -->
