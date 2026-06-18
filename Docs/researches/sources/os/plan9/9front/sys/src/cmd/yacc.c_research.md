# File Research: sources/os/plan9/9front/sys/src/cmd/yacc.c

## Read Status
Complete: 2,954 lines read.

## Purpose
This file is a complete Plan 9 yacc implementation. It reads yacc grammar files, parses declarations and grammar rules, builds LALR-style parser states with lookahead sets, detects and resolves conflicts, packs action/goto tables, and emits generated C parser output using `/sys/lib/yaccpar` or `/sys/lib/yaccpars`.

## Main Responsibilities
- Command-line setup for yacc output: `-v`, `-d`, `-D`, `-o`, `-s`, and `-S`.
- Grammar declaration parsing: tokens, precedence, associativity, types, `%union`, `%start`, and copied code blocks.
- Grammar rule parsing, including embedded actions rewritten as synthetic empty productions.
- Symbol table management for terminals and nonterminals.
- FIRST set and nullable/non-empty derivation analysis.
- LR item closure and state generation.
- Shift/reduce and reduce/reduce conflict reporting and precedence handling.
- Action and goto table generation, packing, optimization, and C array emission.
- Parser skeleton copying and insertion of generated semantic actions.

## Key Data Structures
- `Symb`: symbol name and numeric token/nonterminal value.
- `Lkset`: terminal bitset used for lookahead sets.
- `Item`: LR item pointer plus associated lookahead set.
- `Wset`: temporary working-set item used during closure and state construction.
- Global fixed-size arrays such as `tokset`, `nontrst`, `prdptr`, `pstate`, `lkst`, `amem`, and `mem0` hold most compiler state.

## Important Functions
- `main`: orchestrates setup, grammar analysis, state generation, table output, optimization, and parser skeleton completion.
- `setup`: parses command-line arguments and the yacc input file, builds productions, symbols, type data, and semantic action temp files.
- `gettok`: lexer for yacc grammar syntax, identifiers, string/char literals, declarations, comments, numbers, and section markers.
- `cpyunion`, `cpycode`, `cpyact`: copy user C fragments into output, translating yacc semantic variables like `$$`, `$1`, and `$name`.
- `cpres`, `cempty`, `cpfir`: compute production lists by nonterminal, nullable symbols, and FIRST sets.
- `closure`, `state`, `stagen`: compute closures, canonical states, and gotos.
- `output`, `wract`, `wrstate`, `precftn`: emit per-state actions, diagnose conflicts, and apply precedence/associativity rules.
- `go2out`, `go2gen`: generate nonterminal goto data.
- `callopt`, `stin`, `gin`, `nxti`: table-packing optimizer.
- `others`: writes final parser arrays, token translation tables, generated action code, and parser skeleton.

## Dependencies and Interactions
- Uses Plan 9 headers and runtime APIs: `<u.h>`, `<libc.h>`, `<bio.h>`, `<ctype.h>`.
- Uses `Biobuf` for all main file IO.
- Reads parser skeleton files from `/sys/lib/yaccpar` or `/sys/lib/yaccpars`.
- Writes generated `tab.c`, optional `tab.h`, optional `output`, optional `debug`, and temporary files for actions/tables.
- Uses Plan 9 private-use Unicode token values beginning at `0xE000`.

## Design Notes
- This is an old-style C program built around global fixed-size arrays rather than dynamically sized containers.
- Several comments acknowledge portability constraints, especially reusing `mem0` for both production integers and `Item` storage.
- Error handling is mostly fatal through `error`, which summarizes, removes temp files, and exits.
- The implementation assumes limits such as `NSTATES`, `NPROD`, `NTERMS`, `NNONTERM`, `ACTSIZE`, and `MEMSIZE`; large grammars fail with explicit diagnostics.
- The file is not a filesystem component itself, but it is part of the 9front source tree tooling included in subset A.
