# sources/test-tools/syzkaller/pkg/html/html.go

## Purpose
`html.go` centralizes syzkaller dashboard template creation and formatting helpers shared by HTML and text templates.

## Important APIs, Types, And Functions
`SetGlobSearchPath`, `CreateGlob`, and `CreateTextGlob` manage template loading. `Funcs` exports template functions including link generation, time/date/duration formatting, repro-level rendering, hash truncation, list formatting, pointer dereference, bisect selection, and commit links. Exported `FormatTime` and `FormatDate` provide reusable date strings. Private helpers include `link`, `optlink`, `formatKernelTime`, `formatJSTime`, `formatClock`, `formatDuration`, `formatLateness`, `formatReproLevel`, `formatStat`, `formatShortHash`, `formatTagHash`, `formatCommitTableTitle`, `formatStringList`, `selectBisect`, `dereferencePointer`, and `commitLink`.

## Control Flow
At package load, `globSearchPath` is selected based on `appengine.IsAppEngine()`. `CreateGlob` and `CreateTextGlob` reject path-like globs, join the glob with the configured search path, attach `Funcs`, and parse matching templates. Formatting helpers generally return an empty string for zero values. `formatDuration` emits compact day/hour/minute strings with different precision depending on magnitude. `selectBisect` prefers fix bisection over cause bisection. `dereferencePointer` unwraps a non-nil pointer if the pointed value can be interfaced.

## State And Persistence Behavior
The mutable package-level `globSearchPath` controls future template parsing and can be overridden by tests or callers. No persistent state is written. Template parsing reads files from disk. `runtime.KeepAlive(SetGlobSearchPath)` preserves the externally used setter from dead-code removal assumptions.

## Dependencies And Integration Points
The file depends on Go `html/template` and `text/template`, `appengine`, `dashboard/dashapi` repro and bisect types, and `pkg/vcs` for commit links. It is a foundational dependency for dashboard pages and email/text template rendering.

## Risks And Edge Cases
`link` escapes link text but interpolates the URL directly into an HTML attribute, so callers must avoid untrusted unsafe URLs. `dereferencePointer` calls `IsNil` before checking kind; passing a non-nilable non-pointer interface would panic, so template use must pass pointers or nilable kinds. Template parse failures panic via `template.Must`, appropriate for startup but not for dynamic user input. The global search path is mutable and not synchronized.

## Test Signals
Expected tests should cover formatting edge cases, AppEngine versus local template paths, template helper registration, link escaping, and pointer dereference behavior. This source set does not include direct tests for `html.go`, but `pages/stats_test.go` indirectly exercises embedded template creation and helpers.
