<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/19 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/19

## Purpose
This minimal fixture tests recognition of a KASAN wild-memory-access read without a full stack trace. It expects title `KASAN: wild-memory-access Read`, type `KASAN-READ`, and `CORRUPTED: Y`.

## Important APIs, Types, And Functions
The only fixture API elements are the metadata headers and a short raw KASAN line: `BUG: KASAN: wild-memory-access on address ...`. Parser behavior under test includes sanitizer signature detection, read/write type classification, and corrupted-report handling when no reliable function frame exists.

## Control Flow
`parseReport` reads the three headers and the seven-line log. The Linux reporter must identify the KASAN wild-memory-access text directly and produce a generic read title because there is no stack function to name.

## State And Persistence
Persistent state is extremely compact: title, type, corruption flag, and an address-bearing sanitizer line. The address is dynamic and not semantically stable.

## Dependencies And Integration Points
It integrates with Linux KASAN parser rules and type mapping to `KASAN-READ`. It is useful for boundary testing parser behavior on underspecified reports.

## Risks
The parser could fail to report a crash due to missing stack frames, or it could attempt to embed the volatile address into the title. It could also misclassify the event as generic `MEMORY_SAFETY_BUG` rather than `KASAN-READ`.

## Test Signals
The stable signal is exact title `KASAN: wild-memory-access Read`, type `KASAN-READ`, and corruption true despite the absence of call trace data.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/19 -->
