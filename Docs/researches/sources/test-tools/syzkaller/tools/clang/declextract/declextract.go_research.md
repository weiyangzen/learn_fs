<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/declextract.go -->
# sources/test-tools/syzkaller/tools/clang/declextract/declextract.go

## Purpose

Marker Go package for the declextract Clang implementation.

## Important APIs, Types, and Functions

Exports `const Tool = "declextract"`.

## Control Flow

Shared clangtool runner uses the selector; C++ constructor exits into extractor `Main` when the environment matches.

## State and Persistence Behavior

No mutable state or persistence.

## Dependencies and Integration Points

Used by Go-side declaration extraction wrappers.

## Risks and Edge Cases

String mismatch prevents dispatch to the intended C++ extractor.

## Test Signals

Build and run declextract against a tiny compilation database.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/declextract/declextract.go -->
