# sources/test-tools/syzkaller/pkg/ast/scanner.go

## Purpose
Lexical scanner for syzkaller description syntax.

## Important APIs, Types, and Functions
Defines token constants, punctuation/keyword tables, `scanner`, `ErrorHandler`, `LoggingHandler`, `BuiltinFile`, `Pos` helpers, `newScanner`, `Scan`, token-specific scanners, `IsValidStringLit`, and scanner position/error helpers.

## Control Flow
`Scan` skips spaces/tabs, emits EOF after an implicit newline, captures define C expressions based on previous tokens, scans comments, strings/hex strings, integers, chars, identifiers/keywords, multi-char operators, or punctuation. `next` handles CR stripping, line/column updates, NUL errors, and final newline behavior.

## State and Persistence Behavior
Scanner maintains byte offset, line, column, previous tokens, and error count over an input byte slice. It does not persist data.

## Dependencies and Integration Points
Used by `parser.go`. Error handlers integrate with tests and logging.

## Risks and Test Signals
Risks include byte-oriented column handling, limited char literal support, hex string decoding errors, implicit newline edge cases, and C-expression token context. Parser tests and error fixtures exercise scanner behavior.
