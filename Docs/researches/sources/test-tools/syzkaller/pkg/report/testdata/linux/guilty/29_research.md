# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/29

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `drivers/vhost/vhost.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=drivers/vhost/vhost.c.
- Notable functions observed in the report body: `__list_add_valid`, `__dump_stack`, `dump_stack`, `print_address_description`, `kasan_report_error`, `kasan_report`, `__asan_report_load8_noabort`, `__list_add`.
- Notable source locations observed in the report body: `lib/list_debug.c:23`, `lib/dump_stack.c:17`, `lib/dump_stack.c:53`, `mm/kasan/report.c:252`, `mm/kasan/report.c:351`, `mm/kasan/report.c:409`, `mm/kasan/report.c:430`, `include/linux/list.h:60`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 97 lines and 4542 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `drivers/vhost/vhost.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: KASAN: use-after-free in __list_add_valid+0xb1/0xd0 lib/list_debug.c:23`.
- The expected blamed subsystem prefix is `drivers`; competing frames should not outrank `drivers/vhost/vhost.c`.
