# sources/security-integrity/selinux/libsepol/cil/src/cil_parser.h

## Purpose
`cil_parser.h` declares the CIL parse-tree builder.

## Important APIs, Types, And Functions
It declares `cil_parser`, which takes a source path, mutable input buffer, byte size, and parse tree pointer.

## Control Flow
The header has no runtime flow. The implementation drives lexer tokenization and tree construction.

## State And Persistence Behavior
No state is stored in the header. The function mutates the supplied parse tree and uses interned strings for node data.

## Dependencies And Integration Points
It includes `cil_tree.h`, making the parser API part of the tree-building layer. `cil.c` calls this during file/module loading.

## Risks And Edge Cases
Callers must pass the size expected by the Flex scan buffer setup, including trailing NUL space prepared by the loader. The buffer must be mutable because quoted strings are edited in place.

## Test Signals
Parser unit tests and loader integration tests are the primary signals, especially malformed syntax and source-location reporting.
