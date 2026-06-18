# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/38

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `sound/core/seq/seq_clientmgr.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=sound/core/seq/seq_clientmgr.c.
- Notable functions observed in the report body: `__dump_stack`, `dump_stack`, `nmi_cpu_backtrace.cold.3`, `nmi_trigger_cpumask_backtrace`, `arch_trigger_cpumask_backtrace`, `trigger_single_cpu_backtrace`, `rcu_dump_cpu_stacks`, `print_cpu_stall.cold.78`.
- Notable source locations observed in the report body: `lib/dump_stack.c:77`, `lib/dump_stack.c:113`, `lib/nmi_backtrace.c:101`, `lib/nmi_backtrace.c:62`, `arch/x86/kernel/apic/hw_nmi.c:38`, `include/linux/nmi.h:162`, `kernel/rcu/tree.c:1340`, `kernel/rcu/tree.c:1478`.
- Opcode material: 2 `Code:` line(s), with 2 marked trapping opcode marker(s).

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 61 lines and 3564 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `sound/core/seq/seq_clientmgr.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `rcu: INFO: rcu_sched self-detected stall on CPU`.
- The expected blamed subsystem prefix is `sound`; competing frames should not outrank `sound/core/seq/seq_clientmgr.c`.
