# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/yacc.py

## Purpose
This file is the vendored PLY yacc implementation used by sepolgen's reference-policy parser. It turns grammar functions with BNF docstrings into SLR or LALR(1) parse tables, persists those tables as Python modules or pickles, and exposes an `LRParser` runtime that consumes tokens from the companion lexer. It is infrastructure code rather than SELinux-domain logic, but correctness here controls every parser built on top of `sepolgen.refparser`.

## Important APIs, Types, And Functions
The public construction entry point is `yacc(...)`, with options for parser method, debug output, module/tabmodule selection, start symbol, recursion checks, table writing, output directory, loggers, and pickle files. It uses `ParserReflect` to inspect a grammar module for `tokens`, `precedence`, `start`, `p_error`, and `p_*` production functions.

`LRParser` is the runtime parser. `parse()` dispatches to `parsedebug`, `parseopt`, or `parseopt_notrack` depending on debug and tracking flags. `restart()`, `errok()`, `disable_defaulted_states()`, and the `token` method support parser state control and panic-mode error recovery.

`YaccSymbol` represents parser stack symbols, and `YaccProduction` is the list-like object passed into grammar actions. It exposes values by index, location helpers (`lineno`, `linespan`, `lexpos`, `lexspan`), parser/lexer references, and `error()` which raises `SyntaxError` to trigger recovery.

`Grammar`, `Production`, `MiniProduction`, and `LRItem` model grammar metadata and LR item state. `Grammar` validates productions, precedence, start symbols, undefined symbols, unreachable symbols, unused terminals/rules, infinite recursion, FIRST sets, FOLLOW sets, and LR items.

`LRTable` reads generated table modules or pickle files, validates `__tabversion__`, and binds production names back to callables. `LRGeneratedTable` builds LR(0), SLR, and LALR table data, resolves conflicts with precedence/associativity, records conflict diagnostics, and writes or pickles parse tables.

## Control Flow
`yacc()` obtains a parser namespace from the supplied module or caller stack, resolves the output directory, applies package-qualified tabmodule handling, reflects and validates grammar metadata, computes a grammar signature, and tries to load existing tables. If an optimized or signature-matching table loads, callables are rebound and an `LRParser` is returned.

If no table is reusable, `yacc()` validates parser functions, builds a `Grammar`, registers precedence and productions, checks undefined symbols, unused symbols, unreachable symbols, infinite recursion, and unused precedence, then creates an `LRGeneratedTable`. The generated table is optionally written to a tabmodule or pickle before an `LRParser` is returned.

At parse time, `LRParser` keeps explicit state and symbol stacks. It gets lookahead tokens from either `lexer.token()` or a supplied `tokenfunc`, shifts positive actions, reduces negative actions by invoking the grammar callable with a `YaccProduction`, and returns on action `0`. Syntax errors create or propagate an `error` symbol, call `p_error` once per recovery window, and discard input or pop parser state according to yacc-style panic recovery.

Table generation starts with LR(0) closure and goto sets, then optionally computes LALR lookaheads using nullable nonterminals, nonterminal transitions, DR/READS relations, lookback/includes relations, and the `digraph()` propagation helper. `lr_parse_table()` walks each item set to build action/goto rows and applies conflict resolution.

## State And Persistence
Parser runtime state lives in `statestack`, `symstack`, `lookahead`, `lookaheadstack`, `errorok`, `state`, and defaulted-state maps. Deprecated module globals `_errok`, `_token`, and `_restart` are temporarily rebound while calling old-style `p_error` implementations.

Generated parser state persists as a Python tabmodule containing `_tabversion`, `_lr_method`, `_lr_signature`, `_lr_action`, `_lr_goto`, and `_lr_productions`, or as a pickle with equivalent data. Debug mode writes `parser.out` by default. The module-level global `parse` is rebound to the last built parser's `parse` method, which is a legacy convenience but also global mutable state.

## Dependencies And Integration Points
The file depends only on the Python standard library (`re`, `types`, `sys`, `os.path`, `inspect`, `warnings`, and pickle modules) plus relative import `.lex` at parse time when no lexer is supplied. It is integrated by grammar modules that define `tokens`, optional `precedence`, optional `start`, optional `p_error`, and production functions named `p_*` with grammar docstrings.

The sepolgen tests in this subset indirectly exercise this file through `sepolgen.refparser.parse(...)`, especially interface parsing and interface expansion tests. Table files (`parsetab.py`) and debug output (`parser.out`) are explicitly cleaned by the sepolgen test Makefile.

## Risks And Edge Cases
The code intentionally duplicates parser logic between debug, optimized tracking, and optimized no-tracking paths, so fixes to parser behavior can diverge if not mirrored. Global `parse` and deprecated error-recovery globals are not thread-safe. Table import uses dynamic `exec('import %s' % module)` and therefore depends on trusted module names and Python import path state.

`Grammar.add_production()` uses `eval()` for quoted literal token syntax; that is normal PLY behavior but should remain limited to trusted grammar source. Table loading with `optimize=True` accepts tables without requiring a signature match, which can mask stale grammar/table mismatches. Conflict resolution defaults to shifting unless precedence requires otherwise, so grammar changes can silently alter parse choices while only producing warnings.

## Test Signals
There is no direct unit test for `yacc.py` in this subset. `test_refparser.py`, `test_interfaces.py`, and `test_matching.py` all depend on successful yacc/lexer integration for parsing reference policy interface snippets. The test Makefile removes generated `parser.out` and `parsetab.py`, indicating parser table generation is expected during tests or development runs.
