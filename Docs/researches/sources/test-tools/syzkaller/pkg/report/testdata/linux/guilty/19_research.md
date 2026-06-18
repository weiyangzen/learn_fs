# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/19

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `crypto/af_alg.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=crypto/af_alg.c.
- Notable functions observed in the report body: `at`, `lock_sock`, `af_alg_wait_for_data`, `__do_page_fault`, `slab_alloc`, `__do_kmalloc`, `__kmalloc`, `kfree`.
- Notable source locations observed in the report body: `arch/x86/mm/fault.c:1372`, `include/net/sock.h:1465`, `crypto/af_alg.c:768`, `arch/x86/mm/fault.c:1358`, `mm/slab.c:3378`, `mm/slab.c:3709`, `mm/slab.c:3720`, `mm/slab.c:3800`.

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 36 lines and 2296 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `crypto/af_alg.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: sleeping function called from invalid context at arch/x86/mm/fault.c:1372`.
- The expected blamed subsystem prefix is `crypto`; competing frames should not outrank `crypto/af_alg.c`.
