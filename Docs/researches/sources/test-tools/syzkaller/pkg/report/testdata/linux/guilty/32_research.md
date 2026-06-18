# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/32

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/tipc/name_table.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/tipc/name_table.c.
- Notable functions observed in the report body: `at`, `__list_del_entry_valid`, `__list_del_entry`, `list_del_init`, `tipc_nametbl_unsubscribe`, `tipc_subscrb_subscrp_delete`, `tipc_subscrb_delete`, `tipc_subscrb_release_cb`.
- Notable source locations observed in the report body: `lib/list_debug.c:53`, `lib/list_debug.c:51`, `include/linux/list.h:117`, `include/linux/list.h:159`, `net/tipc/name_table.c:851`, `net/tipc/subscr.c:208`, `net/tipc/subscr.c:238`, `net/tipc/subscr.c:316`.
- Opcode material: 1 `Code:` line(s), with 1 marked trapping opcode marker(s).

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 57 lines and 3103 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/tipc/name_table.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `kernel BUG at lib/list_debug.c:53!`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/tipc/name_table.c`.
