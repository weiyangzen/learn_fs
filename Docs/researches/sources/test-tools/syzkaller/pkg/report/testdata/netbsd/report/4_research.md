# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/4

## Purpose

`sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/4` is a compact NetBSD syzkaller report parser fixture for the expected title `UBSan: Undefined behavior`. It contains a single UBSan diagnostic emitted very early in boot or initialization time, reporting a misaligned `UINT32` store in ACPICA GPE initialization code. The source was read as a complete 3-line file.

## Important APIs, Types, and Functions

The file is static testdata for syzkaller's NetBSD report parser. Parser-facing APIs are the test harness, `Reporter.ContainsCrash`, `Reporter.Parse`, `Reporter.ParseFrom`, the `TITLE:` expectation, and UBSan pattern matching in the NetBSD reporter. Diagnostic entities in the text include `UBSan: Undefined Behavior`, source location `/media/k4iz3n/event1/kWork/src/sys/external/bsd/acpica/dist/events/evgpeinit.c:362:5`, a `store to misaligned address`, target address `0xffffffff85b09a03`, type `UINT32`, and required `4 byte alignment`.

## Control Flow

The test harness reads the title header and passes the single log line to the reporter. The parser must recognize the UBSan diagnostic without needing a stack trace, panic line, stopped debugger frame, or process table. The represented kernel flow is an ACPICA event/GPE initialization path reaching `evgpeinit.c` line 362 and performing a misaligned 32-bit store; the fixture intentionally provides only the sanitizer summary line.

## State and Persistence Behavior

The file persists a minimal expected parser state: title plus one raw UBSan line. Runtime state consists only of the detected crash offset, title, report bytes, and type/classification. There is no process state, lock state, dump state, or file-backed persistence. The absolute build path and kernel address are volatile details and should not be required for stable grouping.

## Dependencies and Integration Points

This fixture integrates with NetBSD UBSan report recognition and with generic syzkaller report handling for one-line crashes. It protects dashboard grouping for undefined-behavior reports that lack a traceback and ensures the parser can use sanitizer category text as the title when no better function frame is available. The kernel-domain integration point is NetBSD's external ACPICA code under `sys/external/bsd/acpica/dist/events`.

## Risks and Edge Cases

The main risk is treating the line as non-crashing because it lacks `panic`, `fatal`, `Stopped`, or stack frames. Another risk is over-specific title extraction that includes the absolute local build path, address, type, or alignment value. The parser should preserve the broad, stable title `UBSan: Undefined behavior`, while retaining detailed location and alignment evidence in the report body.

## Test Signals

A passing test detects this one-line report and returns `UBSan: Undefined behavior` with non-empty report bytes. Useful regression signals are that the parser accepts both `Undefined Behavior` capitalization in the log and `Undefined behavior` capitalization in the expected title, handles sanitizer reports without stack traces, and keeps volatile paths/addresses out of the deduplication title.
