# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/25

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/xfrm/xfrm_ipcomp.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/xfrm/xfrm_ipcomp.c.
- Notable functions observed in the report body: `__this_cpu_preempt_check`, `__dump_stack`, `dump_stack`, `check_preemption_disabled`, `ipcomp_alloc_tfms`, `ipcomp_init_state`, `ipcomp4_init_state`, `__xfrm_init_state`.
- Notable source locations observed in the report body: `lib/smp_processor_id.c:62`, `lib/dump_stack.c:15`, `lib/dump_stack.c:51`, `lib/smp_processor_id.c:46`, `net/xfrm/xfrm_ipcomp.c:286`, `net/xfrm/xfrm_ipcomp.c:363`, `net/ipv4/ipcomp.c:137`, `net/xfrm/xfrm_state.c:2096`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 30 lines and 1970 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/xfrm/xfrm_ipcomp.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: using __this_cpu_read() in preemptible [00000000] code: syzkaller157688/3312`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/xfrm/xfrm_ipcomp.c`.
