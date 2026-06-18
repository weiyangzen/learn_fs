# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/12

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/12` is a NetBSD crash-report fixture for syzkaller's report parser. It encodes an AddressSanitizer/KASAN panic titled `ASan: Unauthorized Access in uvm_fault_internal`, where the first panic line reports an 8-byte read from a freed pool allocation and the stack identifies `uvm_fault_internal()` as the first non-ASan kernel frame after `__asan_load8()`.

The fixture exists to prove that the NetBSD reporter can recognize an `ASan: Unauthorized Access` panic, skip sanitizer frames, derive the crash title from the following functional kernel frame, and preserve enough of the diagnostic body for deduplication and symbolization.

## Important APIs, Types, And Functions

The fixture is consumed by syzkaller's Go test harness rather than by NetBSD itself. The relevant integration points are:

- `ctorNetbsd` in `pkg/report/netbsd.go`, which registers NetBSD oops patterns and stack-line symbolization regexes.
- `netbsdOopses`, especially the `panic: ` group with title pattern `ASan: Unauthorized Access` and report pattern that captures the first stack frame after `kasan` or `__asan`.
- `ctorBSD`, `bsd.Parse`, and `bsd.Symbolize` in `pkg/report/bsd.go`, which provide the common BSD parser and stack-line symbolizer.
- `simpleLineParser` through `bsd.Parse`, which extracts a bounded report from the full VM console transcript.
- `TestReportParse`/`forEachFile` in `pkg/report/report_test.go`, which discovers numbered files under `testdata/netbsd/report`.

The NetBSD frames inside the fixture identify kernel APIs involved in the crash path: `vpanic`, `kasan_report`, `__asan_load8`, `uvm_fault_internal`, and `trap`. The later DDB dump includes process, LWP, lock, page, and pool listings, but those are diagnostic payload rather than parser APIs.

## Control Flow

The crash path represented by the fixture starts with a syzkaller executor faulting in supervisor mode. NetBSD reports a sanitizer panic, enters `vpanic`, emits a timestamped traceback, and stops in DDB at `breakpoint`. The meaningful stack sequence is:

1. `vpanic` emits the panic.
2. `kasan_report` classifies the bad access.
3. `__asan_load8` performs the checked load and detects the invalid freed-pool access.
4. `uvm_fault_internal` is the first substantive kernel frame and becomes the extracted crash-site function.
5. `trap` shows the hardware trap path that led into the fault.

After the initial traceback, the file includes the DDB prompt response with `bt`, register state, process table, lock state, page lists, and pool state. For parser behavior, the opening `TITLE:` and early panic/stack lines are the high-signal region. The long tail is intentionally noisy and validates that the parser does not lose the primary crash identity when the console contains extensive debugger output.

## State And Persistence Behavior

The fixture is static testdata. It persists only as a repository file and has no runtime mutation, external storage, or side effects. Its state-like content is captured kernel state at panic time:

- current LWP `pid 731.1` in `syz-executor.3`;
- register values, including `rip` at `breakpoint+0x5`;
- multiple syzkaller executor LWPs and system threads;
- locks initialized by `uvm_obj_init`, `amap_alloc`, and `vcache_alloc`;
- DDB page and pool snapshots.

This diagnostic state matters because report extraction must tolerate large, repetitive tables and addresses without treating later lines as separate crashes or corrupting the original title.

## Dependencies

The test fixture depends on syzkaller's report-test file convention: a leading `TITLE:` header followed by the raw console log. It is tied to NetBSD-specific output syntax:

- `panic: ASan: Unauthorized Access ...`;
- timestamped traceback lines like `[ 77.2441254]`;
- stack frames in the `function() at netbsd:function+0xoffset file:line` format;
- DDB markers such as `Stopped in pid`, `show registers`, `ps`, and lock/page/pool dumps.

The parser-side dependency is the regular expression in `ctorNetbsd` that symbolization can match: ` at netbsd:([A-Za-z0-9_]+)\+0x([0-9a-f]+)`.

## Integration Points

This file integrates with `go test ./pkg/report` through directory scanning in `forEachFile`. The expected title is embedded in the `TITLE:` header and is compared against the title produced by `Reporter.Parse`. During symbolization tests, stack lines in the report may be rewritten with source file and line information when kernel symbols are available.

The key cross-file relationship is with `pkg/report/netbsd.go`: this fixture validates the ASan branch of `netbsdOopses`, while neighboring fixtures cover other NetBSD crash classes such as lock errors, supervisor faults, MSan, and UBSan.

## Risks

The main parser risk is regex fragility. If NetBSD changes sanitizer wording, stack indentation, `netbsd:` frame formatting, or DDB prompt sequencing, this fixture may stop matching or may extract the wrong frame. The `ASan` report regex is especially sensitive to the assumption that a sanitizer frame appears before the real kernel frame.

Another risk is over-capturing. The DDB dump is very large and contains many function-looking tokens, addresses, and lock owner records. A broad parser could accidentally select a later diagnostic function instead of `uvm_fault_internal`, or include too much low-value dump output in the normalized report.

## Test Signals

The expected test signal is the title `ASan: Unauthorized Access in uvm_fault_internal`. Successful parsing means `ContainsCrash` detects the panic, `Parse` returns a non-nil report with this title, and the report body keeps the relevant sanitizer stack while ignoring unrelated boot or DDB noise. Successful symbolization means NetBSD stack lines with `netbsd:<function>+0x<offset>` remain parseable and can be expanded when symbol data exists.
