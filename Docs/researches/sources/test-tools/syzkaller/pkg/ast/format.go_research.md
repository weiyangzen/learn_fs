# sources/test-tools/syzkaller/pkg/ast/format.go

## Purpose
Serializes AST descriptions and nodes back into syzkaller description syntax.

## Important APIs, Types, and Functions
`Format`, `FormatWriter`, `SerializeNode`, `FormatInt`, `FormatStr`, node `serialize` methods, `fmtType`, `fmtField`, `fmtTypeList`, `fmtExpressionRec`, and `operatorPrio` implement formatting.

## Control Flow
Top-level formatting dispatches through the private `serializer` interface. Structs align field type columns and preserve new blocks/comments. Types serialize atoms, colon parts, arguments, strings/ints, and binary expressions with precedence-aware parentheses.

## State and Persistence Behavior
Writes text to a buffer or writer; does not mutate the AST. Formatting preserves enough layout for round-trip tests but normalizes some spacing/alignment.

## Dependencies and Integration Points
Used by parser round-trip tests and tools that generate or rewrite syzlang descriptions.

## Risks and Test Signals
Unknown node/operator/format values panic. Round-trip tests across all Linux sys files are the main signal for parser/formatter compatibility.
