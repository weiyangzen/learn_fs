## sources/sync-backup/restic/internal/options/secret_string_test.go

Purpose: tests that `SecretString` redacts non-empty secrets across common formatting paths.

Important tests: `TestSecretString` checks `String`, `GoString`, `fmt.Sprint`, `%v`, `%#v`, and `Unwrap`. `TestSecretStringStruct` confirms formatted structs do not contain the secret. `TestSecretStringEmpty` validates empty-string behavior. `TestSecretStringDefault` validates zero-value safety.

Control flow and state: tests use a small struct containing a `SecretString` and helper `assertNotIn` for leak checks.

Dependencies and integration points: uses the public `options` package from an external test package, so exported behavior is tested as consumers see it.

Risks and test signals: tests cover formatting leaks but not JSON/YAML marshaling or custom reflection-based logging.
