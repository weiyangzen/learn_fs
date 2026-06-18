# sources/test-tools/syzkaller/pkg/ast/test_util.go

## Purpose
Test helper for matching parser diagnostics embedded in testdata files.

## Important APIs, Types, and Functions
`ErrorMatcher`, `errorDesc`, `NewErrorMatcher`, `ErrorHandler`, `Count`, `Check`, and `DumpErrors` collect expected and actual errors. `errorLocationRe` normalizes location substrings inside messages.

## Control Flow
`NewErrorMatcher` reads a file, strips `### expected error` annotations while recording line/text expectations. `ErrorHandler` records actual diagnostics. `Check` matches actual errors to expected by line and text, sorts unmatched/unexpected errors by position, and reports a formatted diff.

## State and Persistence Behavior
Stores stripped data and diagnostics in memory. Reads testdata files only.

## Dependencies and Integration Points
Used by `parser_test.go` error-fixture tests.

## Risks and Test Signals
Risks include exact-message brittleness and only line-level expected positions. It provides clear diagnostics when parser error behavior changes.
