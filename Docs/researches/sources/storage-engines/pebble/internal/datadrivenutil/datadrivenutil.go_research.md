# sources/storage-engines/pebble/internal/datadrivenutil/datadrivenutil.go

## Purpose
This file provides small parsing helpers for Pebble datadriven tests, making line, field, key-value, integer, and hex-byte extraction concise.

## Important APIs, Types, And Functions
`Lines.Next` consumes one line at a time. `Line.Fields` splits on whitespace plus optional delimiters. `Fields` supports `String`, `HasValue`, `Index`, `KeyValue`, `MustKeyValue`, and `HexBytes`. `Value` supports `Str`, `Bytes`, `Int`, `Uint64`, and `HexBytes`.

## Control Flow
Parsing is intentionally direct: `Lines.Next` searches for newline and mutates the receiver; `Fields` uses `strings.FieldsFunc`; key-value lookup scans fields for `key=`; numeric and hex conversions panic on invalid data.

## State And Persistence Behavior
State is limited to the mutable `Lines` string wrapper during parsing. There is no persistence.

## Dependencies And Integration Points
It depends on `encoding/hex`, `strconv`, `strings`, `unicode`, and `errors`. Datadriven tests across Pebble can use it to reduce custom parsing boilerplate.

## Risks And Edge Cases
`Fields.KeyValue` indexes `fs[i][len(key)]` after a length check of `>= len(key)`, so an exact field equal to the key without `=` would be risky if encountered; expected usage is `key=value` fields. Panic-on-parse is acceptable for tests but unsuitable for production parsing.

## Test Signals
No direct tests are in this subset. Its behavior is indirectly validated by any datadriven tests using these helpers.
