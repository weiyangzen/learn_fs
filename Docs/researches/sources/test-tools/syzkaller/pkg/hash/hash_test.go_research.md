# sources/test-tools/syzkaller/pkg/hash/hash_test.go

## Purpose
`hash_test.go` provides basic regression coverage for the `hash` package's ability to distinguish different input values.

## Important APIs, Types, And Functions
`TestHash` calls `String` on byte slices, strings, and a small struct type `X{Int int}`.

## Control Flow
The test compares `String([]byte{})` with `String([]byte{0})`, `String("foo")` with `String("bar")`, and `String(X{0})` with `String(X{1})`. Any equality triggers `t.Fatal("equal hashes")`.

## State And Persistence Behavior
The test is pure and in-memory. It relies on deterministic hashing and JSON encoding for the struct case.

## Dependencies And Integration Points
It imports only `testing` and runs in package `hash`, giving direct access to exported helpers. It is a lightweight signal for package consumers that values are not trivially collapsed.

## Risks And Edge Cases
The test does not pin exact hashes, so accidental output format changes could go unnoticed if inequality remains. It does not test multi-piece ambiguity, panic behavior, nil values, or `Truncate64`.

## Test Signals
A failure means `Hash` or `String` is seriously broken for common input classes. Passing does not prove cross-version stability or collision resistance.
