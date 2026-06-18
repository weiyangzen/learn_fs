# sources/sync-backup/kopia/internal/contentlog/contentlog_benchmark_test.go

Purpose: benchmarks the low-allocation content logger across context params, logger params, content ID params, and `Log` through `Log6`.

Important APIs/types/functions: `BenchmarkLogger`, `contentlog.WithParams`, `contentlog.NewLogger`, `Log`, `Log1` through `Log6`, `logparam`, and `contentparam.ContentID`.

Control flow: parses a fixed content index ID, attaches context params, creates a logger with one logger-level param and a sink that discards bytes, then repeatedly emits messages with zero through six strongly typed params inside `b.Loop()`.

State and persistence behavior: benchmark output is discarded; state is pooled JSON writer reuse and context-carried params.

Dependencies/integration: uses `repo/content/index` parsing and logging parameter packages.

Risks/test signals: benchmark checks performance shape but has no assertions about allocation counts in this file. It is useful for catching regressions in generic logging paths when run with Go benchmark allocation reporting.
