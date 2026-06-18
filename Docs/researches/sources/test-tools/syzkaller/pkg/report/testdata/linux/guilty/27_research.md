# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/27

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `sound/core/oss/mulaw.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=sound/core/oss/mulaw.c.
- Notable functions observed in the report body: `sched_show_task`, `print_other_cpu_stall`, `check_cpu_stall.isra.61`, `__rcu_pending`, `rcu_pending`, `rcu_check_callbacks`, `update_process_times`, `tick_sched_handle`.
- Notable source locations observed in the report body: `kernel/sched/core.c:5198`, `kernel/rcu/tree.c:1564`, `kernel/rcu/tree.c:1682`, `kernel/rcu/tree.c:3440`, `kernel/rcu/tree.c:3502`, `kernel/rcu/tree.c:2842`, `kernel/time/timer.c:1628`, `kernel/time/tick-sched.c:162`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 56 lines and 3070 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `sound/core/oss/mulaw.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `INFO: rcu_sched detected stalls on CPUs/tasks:`.
- The expected blamed subsystem prefix is `sound`; competing frames should not outrank `sound/core/oss/mulaw.c`.
