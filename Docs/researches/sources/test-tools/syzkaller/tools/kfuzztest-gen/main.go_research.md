<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/kfuzztest-gen/main.go -->
# sources/test-tools/syzkaller/tools/kfuzztest-gen/main.go

## Purpose

CLI that extracts KFuzzTest metadata from vmlinux and emits syzlang.

## Important APIs, Types, and Functions

`kfuzztest.NewExtractor`, `ExtractAll`, `NewBuilder`, `EmitSyzlangDescription`, `tool.Fail`.

## Control Flow

Validates one arg, extracts ELF metadata, logs summary, builds syzlang description, prints to stdout.

## State and Persistence Behavior

Extractor state until close; no file writes.

## Dependencies and Integration Points

Depends on `pkg/kfuzztest` and vmlinux debug/annotation data.

## Risks and Edge Cases

Output quality depends on kernel metadata; exits on first error.

## Test Signals

Run on known annotated vmlinux and compare syzlang golden output.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/kfuzztest-gen/main.go -->
