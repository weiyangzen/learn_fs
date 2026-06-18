# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/16

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `ipc/util.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=ipc/util.c.
- Notable functions observed in the report body: `at`, `__vunmap`, `__dump_stack`, `dump_stack`, `__panic`, `panic_saved_regs`, `warn_slowpath_common`, `warn_slowpath_fmt`.
- Notable source locations observed in the report body: `mm/vmalloc.c:1473`, `mm/vmalloc.c:1472`, `lib/dump_stack.c:15`, `lib/dump_stack.c:51`, `kernel/panic.c:179`, `kernel/panic.c:280`, `kernel/panic.c:642`, `kernel/panic.c:658`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 18 lines and 890 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `ipc/util.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `WARNING: CPU: 1 PID: 7733 at mm/vmalloc.c:1473 __vunmap+0x1ca/0x300 mm/vmalloc.c:1472()`.
- The expected blamed subsystem prefix is `ipc`; competing frames should not outrank `ipc/util.c`.
