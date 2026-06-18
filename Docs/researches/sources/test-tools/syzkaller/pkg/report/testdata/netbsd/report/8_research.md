# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/8

## Purpose

This three-line NetBSD fixture verifies UBSan detection and title normalization. It expects `UBSan: Undefined behavior` from a one-line undefined-behavior report in an ACPICA table-loading source file.

## Important APIs, Types, and Functions

The relevant reporter APIs are sanitizer-pattern matching, `TITLE:` expectation parsing, and normalized title construction. Kernel/source evidence names `/sys/external/bsd/acpica/dist/tables/tbxfload.c:187:10`, a misaligned load, type `UINT32`, and address/alignment details.

## Control Flow

The parser reads the expected title and then a timestamped UBSan diagnostic. There is no panic stack, DDB prompt, or reboot trailer. The reporter must still classify the sanitizer line as a crash signal and use the generic UBSan title rather than volatile file path, address, or type-specific wording.

## State and Persistence Behavior

The fixture stores the source location, bad address, access type, and required alignment. Those are evidence in the report body, but they are intentionally excluded from the stable title. Runtime parser state is limited to the sanitizer match and report byte range.

## Dependencies and Integration Points

This integrates NetBSD sanitizer recognition with the common syzkaller report pipeline. It also covers early boot or single-line crash evidence, where the parser cannot depend on a subsequent traceback.

## Risks and Edge Cases

Over-specific titles would fragment UBSan bugs by build path or address. Under-detection would miss reports that lack `panic:`. The parser also needs to preserve case-insensitive or capitalization-insensitive matching between `Undefined Behavior` in the log and `Undefined behavior` in the expected title.

## Test Signals

A passing test returns exactly `UBSan: Undefined behavior` and a non-empty report containing the misaligned `UINT32` load diagnostic.
