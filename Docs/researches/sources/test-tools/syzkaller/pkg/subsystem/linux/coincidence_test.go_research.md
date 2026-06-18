# sources/test-tools/syzkaller/pkg/subsystem/linux/coincidence_test.go

## Purpose

This test file validates `CoincidenceMatrix` counting semantics. It ensures the matrix correctly records self-counts as subsystem file totals and ordered pair counts as co-occurrence totals.

## Important APIs, Types, and Functions

`TestCoincidenceMatrix` uses `MakeCoincidenceMatrix`, `Record`, `Count`, `Get`, and `NonEmptyPairs`. It creates three anonymous `subsystem.Subsystem` pointers and uses `testify/assert` for equality and order-insensitive pair comparison.

## Control Flow

The test records `(a,b)` and `(b,c)`. It expects self counts of `1,2,1`, pair counts for `a-b` and `b-c`, and zero for unrelated `a-c`. It then collects all non-self pairs from `NonEmptyPairs` and checks that both directions of each observed relationship are present.

## State, Dependencies, Risks, and Test Signals

The test state is entirely in-memory. Dependencies are `testing`, `github.com/google/syzkaller/pkg/subsystem`, and `testify/assert`. It confirms the bidirectional nature of `Record` and the callback skipping diagonal entries. It does not cover duplicate subsystem pointers passed in one `Record`, nil subsystem pointers, or concurrent use, so those behaviors are left to caller discipline.
