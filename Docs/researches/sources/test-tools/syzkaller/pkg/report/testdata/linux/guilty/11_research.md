# Research: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/11

## Purpose
This fixture is a Linux guilty-file extraction case. `TestGuiltyFile` parses the report, calls `Reporter.Symbolize`, and expects `linux.extractGuiltyFile` to resolve `virt/kvm/eventfd.c` as the blamed source path.
The body is already symbolized enough for `ReportToGuiltyFile` and stack-frame ranking; the test exercises skip lists, sanitizer-frame handling, nested stack sections, and deepest-path selection.

## Important APIs, Types, And Functions
- Exercised APIs/types: `TestGuiltyFile`, `parseGuiltyTest`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.extractGuiltyFile`, `linux.extractGuiltyFileRaw`, `linux.extractGuiltyFileImpl`, `ReportToGuiltyFile`.
- Fixture metadata: FILE=virt/kvm/eventfd.c.
- Notable functions observed in the report body: `__list_del`, `list_del`, `irq_bypass_unregister_consumer`, `irqfd_shutdown`, `process_one_work`, `worker_thread`, `kthread`, `ret_from_fork`.
- Notable source locations observed in the report body: `include/linux/list.h:89`, `include/linux/list.h:107`, `virt/lib/irqbypass.c:258`, `arch/x86/kvm/../../../virt/kvm/eventfd.c:145`, `kernel/workqueue.c:2096`, `kernel/workqueue.c:2230`, `kernel/kthread.c:209`, `arch/x86/entry/entry_64.S:433`.
- Opcode material: 1 `Code:` line(s), with 1 marked trapping opcode marker(s).

## Control Flow
- The guilty-file test reads `FILE:` as the expected answer and passes the remaining report through `Reporter.Parse`; if parser trimming removed symbolized context, the test restores the full fixture body into `rep.Report`.
- `Reporter.Symbolize` invokes Linux symbolization and then `extractGuiltyFile`, which skips generic helpers and sanitizer scaffolding, tracks the first plausible frame, and prefers deeper paths that stay under the same subsystem.

## State And Persistence
- Static fixture only: 48 lines and 2815 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on Linux reporter parsing, Linux symbolization/guilty-frame heuristics, maintainer-path extraction rules, and the `guiltyFileIgnores`/`guiltyLineIgnore` filters in `linux.go`.

## Risks And Edge Cases
- Guilty-file extraction is heuristic: sanitizer wrappers, fault-injection frames, inline frames, IRQ/NMI sections, and repeated subsystem paths can hide the real first actionable file.

## Test Signals
- Primary signal: expected guilty file `virt/kvm/eventfd.c` after parse/symbolize.
- Regression signal: `go test ./pkg/report -run TestGuiltyFile` should still resolve this exact file path despite surrounding sanitizer, syscall, IRQ, or helper frames.

## Source-Specific Observations
- First crash/log signal: `FILE: virt/kvm/eventfd.c`.
- The expected blamed subsystem prefix is `virt`; competing frames should not outrank `virt/kvm/eventfd.c`.
