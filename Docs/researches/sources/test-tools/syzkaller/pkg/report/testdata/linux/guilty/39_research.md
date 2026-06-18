# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/39

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `security/apparmor/policy_ns.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=security/apparmor/policy_ns.c.
- Notable functions observed in the report body: `sock_common_setsockopt`, `__sys_setsockopt`, `__do_sys_setsockopt`, `__se_sys_setsockopt`, `__x64_sys_setsockopt`, `do_syscall_64`, `memcmp`, `__dump_stack`.
- Notable source locations observed in the report body: `net/core/sock.c:3038`, `net/socket.c:1902`, `net/socket.c:1913`, `net/socket.c:1910`, `arch/x86/entry/common.c:290`, `lib/string.c:861`, `lib/dump_stack.c:77`, `lib/dump_stack.c:113`.
- Opcode material: 2 `Code:` line(s), with 2 marked trapping opcode marker(s).

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 77 lines and 4254 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `security/apparmor/policy_ns.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `BUG: KASAN: global-out-of-bounds in memcmp+0xe3/0x160 lib/string.c:861`.
- The expected blamed subsystem prefix is `security`; competing frames should not outrank `security/apparmor/policy_ns.c`.
