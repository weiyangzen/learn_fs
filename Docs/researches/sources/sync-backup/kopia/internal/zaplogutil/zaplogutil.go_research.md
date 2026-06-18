<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/zaplogutil/zaplogutil.go -->
# sources/sync-backup/kopia/internal/zaplogutil/zaplogutil.go

- Purpose: Provides reusable zap logging utilities and Kopia console encoder.
- Important APIs/types/functions: `PreciseLayout`, `PreciseTimeEncoder`, `Clock`, `TimezoneAdjust`, `NewStdConsoleEncoder`, `StdConsoleEncoderConfig`, `stdConsoleEncoder`, `Clone`, `EncodeEntry`.
- Control flow: Time helpers wrap zap encoders/clocks. The console encoder builds a line with optional time, level, logger name, message, and structured JSON fields, then appends newline.
- State and persistence: Uses a global zap buffer pool; no durable state.
- Dependencies and integration points: Used by test logging and application logging configuration; integrates `clock`, `zapcore`, and `zap/buffer`.
- Risks and edge cases: Colored output assumes ANSI support; structured field output depends on JSON encoder behavior.
- Test signals: Indirectly covered through logging tests/usages; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/zaplogutil/zaplogutil.go -->
