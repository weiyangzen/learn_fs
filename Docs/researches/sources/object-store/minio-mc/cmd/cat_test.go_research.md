# sources/object-store/minio-mc/cmd/cat_test.go

## Purpose

`cat_test.go` tests `prettyStdout`, the terminal-safe writer used by `mc cat`.

## Important APIs, Types, and Functions

`TestPrettyStdout` copies test strings through `newPrettyStdout` into a buffer and compares expected output.

## Control Flow

The table-driven test covers empty text, plain text, CRLF, tabs/newlines, Unicode, ANSI escape sequences, clear-screen control sequence, and random bytes. It verifies copy byte count and final buffer content.

## State and Persistence Behavior

No persistence is involved; the test uses in-memory readers and buffers.

## Dependencies and Integration Points

It tests `prettyStdout.Write` from `cat-main.go`, indirectly guarding terminal output safety for `mc cat`.

## Risks and Edge Cases

The test expects invalid byte sequences to be transformed according to Go UTF-8 decoding behavior. It does not test partial writes or writer errors.

## Test Signals

The main signal is exact output substitution for control bytes and preservation of printable/space Unicode.
