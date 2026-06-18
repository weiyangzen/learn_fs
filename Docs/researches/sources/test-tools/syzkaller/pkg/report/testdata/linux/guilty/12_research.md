# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/12

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `net/llc/llc_sap.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=net/llc/llc_sap.c.
- Notable functions observed in the report body: `skb_set_owner_r`, `__sock_queue_rcv_skb`, `sock_queue_rcv_skb`, `llc_sap_state_process`, `llc_sap_rcv`, `llc_sap_handler`, `llc_rcv`, `__netif_receive_skb_core`.
- Notable source locations observed in the report body: `include/linux/skbuff.h:2389`, `net/core/sock.c:425`, `net/core/sock.c:451`, `net/llc/llc_sap.c:220`, `net/llc/llc_sap.c:294`, `net/llc/llc_sap.c:434`, `net/llc/llc_input.c:208`, `net/core/dev.c:4190`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 54 lines and 2549 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `net/llc/llc_sap.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `kernel BUG at ./include/linux/skbuff.h:2389!`.
- The expected blamed subsystem prefix is `net`; competing frames should not outrank `net/llc/llc_sap.c`.
