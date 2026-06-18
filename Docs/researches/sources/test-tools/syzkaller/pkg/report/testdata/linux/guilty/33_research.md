# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/33

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `kernel/bpf/cpumap.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=kernel/bpf/cpumap.c.
- Notable functions observed in the report body: `at`, `kvmalloc_node`, `__dump_stack`, `dump_stack`, `panic`, `__warn`, `report_bug`, `fixup_bug.part.11`.
- Notable source locations observed in the report body: `mm/util.c:403`, `lib/dump_stack.c:17`, `lib/dump_stack.c:53`, `kernel/panic.c:183`, `kernel/panic.c:547`, `lib/bug.c:184`, `arch/x86/kernel/traps.c:178`, `arch/x86/kernel/traps.c:247`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 45 lines and 2694 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `kernel/bpf/cpumap.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `WARNING: CPU: 1 PID: 4183 at mm/util.c:403 kvmalloc_node+0xc3/0xd0 mm/util.c:403`.
- The expected blamed subsystem prefix is `kernel`; competing frames should not outrank `kernel/bpf/cpumap.c`.
