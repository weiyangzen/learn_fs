# sources/storage-engines/pebble/internal/strparse/strparse.go

## Purpose
This package implements a panic-on-error token parser for test and debug string formats. It is intended for parsers such as manifest debug parsing that recover panics and convert them to errors.

## Important APIs, Types, and Functions
`Parser` stores the original input, remaining tokens, and last token for diagnostics. `MakeParser(separators,input)` splits input by whitespace and caller-specified separator runes, preserving byte offsets. Basic methods include `Done`, `Offset`, `Peek`, `Next`, `ExpectAll`, `Remaining`, and `Expect`. Domain parsers include `TryLevel`, `Level`, `Int`, `Uint64`, `Uint32`, `SeqNum`, `HashSeqNum`, `SeqNumRange`, `BlobFileID`, `FileNum`, `DiskFileNum`, `InternalKey`, and `UserKeyBounds`. `BracketedRange` collects a bracketed interval string. `Errf` panics with an annotated Cockroach error.

## Control Flow and State
Tokenization scans the input string, skipping whitespace, emitting single-character separators, and emitting non-whitespace token runs up to the next whitespace or separator. Parser methods consume tokens by reslicing `p.tokens`; `Peek` updates `lastToken` even without consuming. Parse failures call `Errf`, so callers must recover if they want ordinary error returns. There is no persistence.

## Dependencies and Integration
The package uses `regexp`, `strconv`, `strings`, `unicode`, Cockroach errors, and Pebble `base` parsing types. It is used by datadriven tests and debug parsers, including `tombspan_test.go` in this work item.

## Risks and Edge Cases
Because methods panic, direct use in production paths would be risky unless recovered. `TryLevel` compiles its regexp on each call, which is fine for tests but inefficient. `BracketedRange` does not explicitly error if the closing bracket is absent; it returns the accumulated string. Offset tracking is byte-based, not rune-index-based, which is typical for Go strings but important for Unicode input.

## Test Signals
`strparse_test.go` validates token offsets, robust `HashSeqNum` diagnostics, and malformed sequence-number ranges. The tests specifically guard against out-of-bounds panics escaping from lower-level sequence parsing.
