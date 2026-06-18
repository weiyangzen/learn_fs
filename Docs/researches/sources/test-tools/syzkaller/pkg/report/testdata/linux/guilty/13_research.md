# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/13

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/dccp/ipv6.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/dccp/ipv6.c.
- Notable functions observed in the report body: `skb_pfmemalloc`, `skb_clone`, `__dump_stack`, `dump_stack`, `kasan_object_err`, `print_address_description`, `kasan_report_error`, `kasan_report.part.1`.
- Notable source locations observed in the report body: `include/linux/skbuff.h:829`, `net/core/skbuff.c:1029`, `lib/dump_stack.c:15`, `lib/dump_stack.c:51`, `mm/kasan/report.c:162`, `mm/kasan/report.c:200`, `mm/kasan/report.c:289`, `mm/kasan/report.c:311`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 63 lines and 3174 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/dccp/ipv6.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: KASAN: use-after-free in skb_pfmemalloc include/linux/skbuff.h:829 [inline] at addr ffff88003b910d8c`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/dccp/ipv6.c`.
