# File Research: sources/os/plan9/9front/sys/src/cmd/forp/dat.h

## Purpose
Defines the core data model for the `forp` formula prover.

## Key Elements
Declares source `Line`, compressed-trie symbol table nodes, `Symbol` records for bit vectors, AST `Node` records, symbol/AST/operator enums, signed-symbol flag, and fmt type checks for expression, AST, and operator formatting.

## Dependencies
Requires Plan 9 `mpint` for numeric literals and the other `forp` modules for construction/conversion.

## Behavior/Risks
`Symbol` embeds `TrieHead`, allowing trie leaves to be cast to symbols. Operator enum values are shared across parser, converter, and formatting tables and must stay synchronized.
