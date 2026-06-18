# sources/test-tools/syzkaller/pkg/ast/parser_test.go

## Purpose
Round-trip and error tests for the syzkaller AST parser/formatter/walker/clone/filter stack.

## Important APIs, Types, and Functions
`TestParseAll`, `TestParse`, `TestErrors`, `parseTests`, and `NewErrorMatcher` are used. The tests call `Parse`, `Format`, `Clone`, `Walk`, `Recursive`, `PostRecursive`, `SerializeNode`, and `Filter`.

## Control Flow
`TestParseAll` parses every Linux sys file and a broad test file, formats and reparses, compares node equality, checks clone formatting, validates walking counts and node info, and tests filters. `TestErrors` compares expected inline `###` diagnostics against parser output.

## State and Persistence Behavior
Reads repository sys/testdata files and stores diagnostics in memory. No writes.

## Dependencies and Integration Points
High-level integration coverage for scanner, parser, formatter, clone, filter, and walk.

## Risks and Test Signals
Very strong regression signal for syzlang syntax support. It can be sensitive to intentional formatting changes and sys description corpus changes.
