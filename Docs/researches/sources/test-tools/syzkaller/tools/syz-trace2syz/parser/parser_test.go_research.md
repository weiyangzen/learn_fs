# sources/test-tools/syzkaller/tools/syz-trace2syz/parser/parser_test.go

## Purpose
This file tests strace parsing into the intermediate trace tree for `syz-trace2syz`.

## Important APIs, types, and functions
- `TestParseLoopBasic` covers ordinary calls, hex/negative/question returns, unfinished/resumed calls, flags, grouped args, arithmetic, and arrows.
- `TestEvaluateExpressions` validates numeric constant parsing/evaluation for hex, decimal, octal, bitwise, shifts, arithmetic, parentheses, and underflow semantics.
- `TestParseLoopPid`, `TestParseLoop1Child`, `TestParseLoop2Childs`, and `TestParseLoop1Grandchild` validate PID parsing and clone-derived process tree relationships.
- `TestParseGroupType` validates bracket/brace group parsing.

## Control flow
Each test builds small inline strace snippets, calls `ParseData`, and inspects `RootPid`, trace lengths, call names, constant values, `Ptree`, or argument dynamic types.

## State and persistence behavior
No persistent state. The blank `sys` import registers syzkaller descriptions for any downstream parser/prog interactions needed by the package.

## Dependencies and integration points
Directly tests `parser.ParseData` and IR types from the same package. It indirectly validates generated lexer/parser code.

## Risks and edge cases
Tests use `t.Fatal` inside loops without including the test string in many failure messages, which can slow diagnosis. Coverage is focused on accepted examples; malformed lines, scanner overlong lines, escaped string decoding, and resumed-without-paused panics are not covered.

## Test signals
Strong regression signal for core parser behavior, especially expression evaluation and process-tree construction. Missing negative/error-path tests are the main gap.
