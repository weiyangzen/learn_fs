<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testlogging/ctx.go -->
# sources/sync-backup/kopia/internal/testlogging/ctx.go

- Purpose: Builds test contexts with Kopia loggers that write to `testing.T`.
- Important APIs/types/functions: `testingT`, `Level`, `LevelDebug`, `LevelInfo`, `LevelWarn`, `LevelError`, `NewTestLogger`, `Context`, `ContextForCleanup`, `ContextWithLevel`, `ContextWithLevelAndPrefix`, `ContextWithLevelAndPrefixFunc`.
- Control flow: Functions wrap a test context with `logging.WithLogger` and module-specific `PrintfLevel` loggers; cleanup contexts use `context.WithoutCancel`.
- State and persistence: No durable state; logger behavior is carried in context values.
- Dependencies and integration points: Integrates `repo/logging`, zap levels, and Go test cleanup patterns.
- Risks and edge cases: Cleanup contexts deliberately ignore cancellation, so cleanup operations can continue after test context cancellation.
- Test signals: Used throughout tests in this subset; no direct unit test.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testlogging/ctx.go -->
