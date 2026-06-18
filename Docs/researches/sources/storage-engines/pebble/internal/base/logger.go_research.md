# sources/storage-engines/pebble/internal/base/logger.go

Purpose: Defines logging and tracing interfaces plus default, in-memory, and no-op implementations.

APIs and types: `Logger`, `DefaultLogger`, `InMemLogger`, `LoggerAndTracer`, `LoggerWithNoopTracer`, and `NoopLoggerAndTracer`.

Control flow and state: `defaultLogger` writes info/error messages to stderr/stdout style streams and panics/exits through fatal logging behavior. `InMemLogger` stores formatted lines in a mutex-protected buffer and panics on fatal. Tracer methods emit events only when wrapping a real tracer; noop implementations discard everything.

Persistence and dependencies: No persistent state. Depends on context, synchronization, and tracing/redaction facilities.

Integration points: Pebble options use these interfaces for logs and slow operation tracing; tests use `InMemLogger` to assert messages.

Risks: Fatal behavior terminates or panics depending on implementation. In-memory logs can grow without bound in long tests if not reset.

Test signals: No paired test here, but many package tests use the interfaces.
