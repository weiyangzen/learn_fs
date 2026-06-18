<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/codesearch.go -->
# sources/test-tools/syzkaller/tools/clang/codesearch/codesearch.go

## Purpose

Marker Go package for the codesearch Clang implementation.

## Important APIs, Types, and Functions

Exports `const Tool = "codesearch"` in package `clangtoolimpl`.

## Control Flow

Go wrappers pass this selector to `pkg/clangtool`; the C++ constructor runs only when `SYZ_RUN_CLANGTOOL` matches it.

## State and Persistence Behavior

No mutable state or persistence.

## Dependencies and Integration Points

Used by `tools/syz-codesearch` to launch the correct C++ tool.

## Risks and Edge Cases

String mismatch with C++ dispatch would build but not execute the intended indexer.

## Test Signals

Build/run `syz-codesearch index` against a small compile database.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/clang/codesearch/codesearch.go -->
