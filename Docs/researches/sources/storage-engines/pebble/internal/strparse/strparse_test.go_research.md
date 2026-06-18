# sources/storage-engines/pebble/internal/strparse/strparse_test.go

## Purpose
This file tests tokenization offsets and error quality for sequence-number parsing helpers.

## Important APIs, Types, and Functions
`TestParserOffsets` checks `MakeParser` output tokens and offsets for whitespace and separator combinations. `TestHashSeqNum` verifies a valid `#42` parse and invalid cases for missing prefix, empty number, and wrong token. `TestSeqNumRangeMalformed` verifies malformed ranges produce `Errf`-formatted errors rather than low-level panics.

## Control Flow and State
The invalid tests use deferred `recover` and assert that the recovered value is an error containing expected context. Parser state is local to each subtest.

## Dependencies and Integration
The test imports `strings`, `testing`, Pebble `base`, and `testify/require`. It targets the parser's role as a debug/test utility that must produce clear errors for malformed datadriven input.

## Risks and Gaps
The tests do not cover `BracketedRange` missing-close behavior, level parsing variants, blob/file number parsing, or Unicode offset semantics. They focus on recently fragile error paths.

## Test Signals
The strongest signal is that parser panics should be recoverable `error` values with the original input embedded in the message.
