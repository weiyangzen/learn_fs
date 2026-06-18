# sources/test-tools/syzkaller/pkg/serializer/serializer_test.go

## Purpose

This test checks the exact textual format emitted by `serializer.Write`.

## Important APIs, Types, And Flow

`TestSerializer` builds a nested `*X` value containing embedded struct `Y`, pointer fields, a slice of structs, booleans, escaped strings, an enum-like named int, a heterogeneous `[]any`, typed nils, named primitive aliases, and a nil function. It writes into a `bytes.Buffer` and compares to a fixed expected string.

## State, Dependencies, Risks, And Test Signals

The test is deterministic and uses `testify/require`. It is intentionally golden-output sensitive, catching formatting changes in commas, newlines, address markers, type names, and interface wrapping. It does not cover panic cases for unsupported kinds or default-field omission in named-field mode beyond the selected fixture.
