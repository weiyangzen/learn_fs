# sources/security-integrity/fscrypt/util/errors.go

Purpose: This utility file centralizes small error-handling helpers for fscrypt, including sticky readers/writers, length validation, system error classification, logic-error panic checks, and integration-test filesystem root discovery.

Important APIs and functions: `ErrReader` wraps `io.Reader` and uses `io.ReadFull` until the first error, then returns the same stored error on later reads. `ErrWriter` mirrors that behavior for writes. `CheckValidLength`, `SystemError`, `NeverError`, `TestRoot`, and `ErrSkipIntegration` are small cross-package helpers.

Control flow and state: `ErrReader` and `ErrWriter` persist only the first error. `TestRoot` reads `TEST_FILESYSTEM_ROOT` and returns `ErrSkipIntegration` if it is unset.

Dependencies and integration points: Used by binary parsing/serialization paths and integration tests; depends on standard `io`, `log`, `os`, and `github.com/pkg/errors`.

Risks and test signals: Sticky read/write helpers simplify call sites but can hide partial-write semantics if callers ignore returned byte counts. Tests should cover first-error retention, short reads via `ReadFull`, valid/invalid lengths, and unset integration-test environment behavior.
