# sources/test-tools/syzkaller/pkg/report/testdata/linux/symbolize/1

## Purpose

This source file is a Linux syzkaller symbolization fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/symbolize/1`. It records expected title `possible deadlock in fakeName` and type `LOCKDEP` while also carrying a `REPORT:` oracle. The fixture verifies that the Linux reporter can parse a raw lockdep report containing the C++ symbol `_Z8fakeNameiii`, run `Reporter.Symbolize`, demangle it to `fakeName`, and keep the extracted report text aligned with the expected post-symbolization block.

## Important APIs, Types, and Functions

The important APIs and data types are `TestSymbolize`, `parseReport`, `Reporter.Parse`, `Reporter.Symbolize`, `linux.symbolize`, `symbolizeLine`, the symbolizer cache, C++/Rust demangling, report-prefix accounting, and `ParseTest.Equal`. Expected parser fields are: title `possible deadlock in fakeName`, type `LOCKDEP`, frame `none`, alternate titles none, flags `none`, executor `proc=5, id=7376`, and explicit report block `yes`. Representative symbols or frames visible to the parser are:

- `_Z8fakeNameiii`
- `nbd_start_device`
- `lock_acquire`
- `blk_alloc_queue`
- `__blk_mq_alloc_disk`
- `nbd_dev_add`
- `nbd_init`
- `do_one_initcall`
- `do_initcall_level`
- `do_initcalls`

## Control Flow

`TestSymbolize` reads the same header/log/report format as parse tests, calls `Reporter.Parse` on the raw log, then invokes `Reporter.Symbolize`. The Linux symbolization path rewrites matching stack lines, demangles C++ names, preserves prefix offsets, and finally compares both derived headers and the `REPORT:` body against this file. The fixture has 306 total lines, 168 log lines, 133 expected report lines, and 15200 bytes. Salient log lines include:

- [  492.198599][T24950] WARNING: possible circular locking dependency detected

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux console-prefix parsing, task/cpu context detection, lockdep report extraction, `symbolizer.Symbolizer` callbacks, demangling via the Linux reporter, report-prefix length tracking, and executor extraction from `syz.5.7376`. The kernel-side text models block/NBD, generic netlink, mutex/lockdep, and syscall frames; these are dependencies only as strings consumed by parser regexes.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. Symbolization must not double-symbolize, corrupt prefix offsets, or leave `_Z8fakeNameiii` unmangled when the expected report uses `fakeName`. Because the fixture has an explicit `REPORT:` block, report extraction must match the body text, not merely the header fields.

## Test Signals

The key test signal is `TestSymbolize`: after parse and symbolization, `ParseTest.Equal` must accept the title/type/executor fields and the extracted `rep.Report` must equal the `REPORT:` oracle. A failure usually means broken demangling, dropped lockdep body lines, wrong report-prefix accounting, or accidental double symbolization.
