# sources/sync-backup/kopia/snapshot/policy/optional.go

Purpose: provides pointer-friendly optional scalar wrappers for policy fields.

Important APIs/types/functions: `OptionalBool`, `OptionalInt`, and `OptionalInt64` types each expose `OrDefault`; constructors are `NewOptionalBool`, `newOptionalInt`, and `newOptionalInt64`.

Control flow: `OrDefault` checks nil pointer and returns the supplied default; otherwise converts the pointed value to the base type.

State and persistence behavior: used as pointer fields in policy structs so JSON can distinguish unspecified, explicit zero/false, and non-zero/true values.

Dependencies/integration: used across retention, error handling, files, scheduling, upload, and other policy packages.

Risks: only bool constructor is exported; tests and package internals use unexported int constructors. Consumers outside the package must allocate integer pointers manually or use higher-level APIs.

Test signals: error-handling tests verify optional bool merge semantics; other optional types are indirectly exercised by policy manager tests.
