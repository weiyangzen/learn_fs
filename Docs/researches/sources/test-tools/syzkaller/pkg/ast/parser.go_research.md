# sources/test-tools/syzkaller/pkg/ast/parser.go

## Purpose
Recursive-descent parser for syzkaller syscall description files.

## Important APIs, Types, and Functions
Public APIs are `Parse` and `ParseGlob`. Private parser methods handle top-level recovery, declarations, calls, structs/unions, flags, typedefs, fields, comments, resources, includes, type expressions, type lists, identifiers, strings, integers, and C expressions.

## Control Flow
`Parse` scans tokens until EOF, recovers per line on parse errors, normalizes blank lines around structs, and returns nil if the scanner recorded errors. `ParseGlob` reads all matching files and appends parsed nodes. Type parsing uses precedence levels for `||`, comparisons, and `&`; factor parsing handles parentheses, ints, identifiers, strings, colon suffixes, and type arguments.

## State and Persistence Behavior
Parser state is current token/literal/position plus scanner state. It builds an in-memory `Description`; no writes except error callbacks.

## Dependencies and Integration Points
Depends on `scanner.go`, AST node definitions, filesystem glob/read, and error handlers. It is central to syzlang compilation and tests.

## Risks and Test Signals
Risks include recovery skipping too much, precedence bugs, C-expression capture after define, newline normalization drift, and nil returns after partial glob failures. Tests parse all Linux descriptions and error fixtures.
