# sources/test-tools/syzkaller/tools/syz-trace2syz/parser/strace.go

## Purpose
This generated goyacc parser implements the `strace.y` grammar for converting lexer tokens into `Syscall` and `IrType` values.

## Important APIs, types, and functions
- `StraceSymType` is the semantic value union for token data, integers, constants, buffer/group types, type slices, and syscall results.
- Token constants mirror `strace.y` declarations.
- Parser tables (`StraceAct`, `StracePact`, `StraceR1`, `StraceR2`, etc.) drive generated parsing.
- `StraceLexer`, `StraceParser`, `StraceParserImpl`, `StraceNewParser`, `StraceParse`, `StraceTokname`, `StraceStatname`, `StraceErrorMessage`, and `Stracelex1` form the parser API.
- The large reduction switch contains grammar actions from `strace.y`, constructing `NewSyscall`, `Constant`, `GroupType`, and `BufferType` values.

## Control flow
`StraceParse` creates a parser and calls `Parse`. The parser repeatedly shifts lexer tokens, reduces grammar productions, and writes the parsed syscall into `Stracelex.(*Stracelexer).result`. Productions cover unfinished and resumed syscalls, optional PIDs, numeric/question/flag returns, argument lists, parenthetical suffixes, constants, groups, field assignments, and buffers.

## State and persistence behavior
Parser state is stack-local plus the receiver's lookahead fields. The parsed result is stored in the lexer object. There is no persistent state. Debug verbosity is controlled by package globals `StraceDebug` and `StraceErrorVerbose`.

## Dependencies and integration points
Generated from `strace.y`; should be regenerated rather than manually edited. It depends on local IR constructors and is invoked by `parser.go`. It is paired with the Ragel-generated lexer in `lex.go`.

## Risks and edge cases
Manual edits will be overwritten by generation. Parser actions type-assert the lexer to `*Stracelexer`, so alternate lexer implementations must still use that concrete type or actions panic. Error messages are generic unless verbose mode is enabled. Resumed call merging assumptions live in `Trace.add`, not this parser.

## Test signals
`parser_test.go` exercises this generated parser indirectly. The authoritative grammar source `strace.y` is easier to review for intended behavior.
