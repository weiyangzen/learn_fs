# sources/storage-engines/pebble/objstorage/remote/logging.go

Purpose: This file wraps any `remote.Storage` implementation with operation logging for data-driven tests and debugging.

Important types and functions: `WithLogging` returns a `loggingStore`. It logs `Close`, `ReadObject`, reader `ReadAt`/`Close`, `CreateObject`, writer `Write` byte counts/`Close`, `List`, `Delete`, and `Size`. `loggingReader` and `loggingWriter` wrap object readers and writers. `errOrPrintf` renders either an error or formatted success detail.

Control flow: Each storage method calls the wrapped method and logs inputs plus success/error details. `List` sorts a copy of returned names for deterministic log output while preserving the original order returned to callers. Writer logging accumulates bytes written and emits the count on close.

State and persistence: The wrapper persists no object data and owns no independent resources; state is limited to the wrapped storage reference, log function, reader/writer names, and writer byte counts.

Dependencies and integration: Provider data-driven tests wrap `remote.NewInMem` with this logger to produce stable expected output for object creation, ref marker creation, listing, deletion, and reads.

Risks and test signals: Logging changes can break data-driven fixtures even when behavior is correct. The wrapper assumes the log callback is safe to call from the relevant goroutines. It delegates `IsNotExistError` directly to the wrapped storage, preserving provider error classification.
