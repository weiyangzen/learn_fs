<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testlogging/printf.go -->
# sources/sync-backup/kopia/internal/testlogging/printf.go

- Purpose: Adapts printf-style functions such as `testing.T.Logf` into zap sugared loggers.
- Important APIs/types/functions: `Printf`, `PrintfLevel`, `PrintfFactory`, `printfWriter`, `Write`, `Sync`.
- Control flow: Builds a zap core with Kopia console encoder and a writer that trims trailing newlines and prefixes messages before calling the provided printf function.
- State and persistence: Stateless aside from the writer's function and prefix fields.
- Dependencies and integration points: Integrates `zap`, `zapcore`, `zaplogutil`, and `repo/logging`.
- Risks and edge cases: Output formatting depends on the custom console encoder; `Sync` is a no-op because test loggers do not need flush.
- Test signals: Indirectly exercised by test contexts and helper output.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testlogging/printf.go -->
