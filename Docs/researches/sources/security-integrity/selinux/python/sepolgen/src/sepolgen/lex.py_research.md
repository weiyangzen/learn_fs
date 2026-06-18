# sources/security-integrity/selinux/python/sepolgen/src/sepolgen/lex.py

## Purpose
This file is the bundled PLY lexer implementation used by sepolgen's reference-policy parser. It builds a stateful token scanner from `tokens`, `literals`, `states`, and `t_*` rule definitions supplied by a caller module or object, then exposes the familiar `input()` and `token()` runtime API.

## Important APIs, Types, And Functions
`LexToken` is the mutable token record carrying `type`, `value`, `lineno`, and `lexpos`. `LexError` reports scanner failures. `Lexer` owns compiled regex tables, state stacks, ignored characters, error/eof callbacks, input text, cursor position, and table serialization via `writetab()` / `readtab()`. Its public control surface is `input`, `token`, `begin`, `push_state`, `pop_state`, `skip`, `clone`, and iteration.

`LexerReflect` introspects the caller dictionary, validates `tokens`, `literals`, `states`, rule functions, rule strings, `t_error`, and `t_eof`, and detects duplicate rules from module source. `_form_master_re()` composes named regex alternatives, recursively splitting large patterns when Python cannot compile the combined expression. `lex()` is the builder entry point and installs module globals `lexer`, `token`, and `input`. `TOKEN` / `Token` attach regex strings to rule functions.

## Control Flow
Build flow starts in `lex()`: gather caller symbols, reflect and validate them unless optimized, optionally read a cached lextab, build per-state master regexes, inherit `INITIAL` expressions for inclusive states, install ignore/error/eof tables, and optionally write a lextab. Runtime flow in `Lexer.token()` loops over input, skips ignored characters, tries each state regex, constructs a `LexToken`, dispatches rule functions when present, validates returned token types in non-optimized mode, handles literals, calls error handlers, and emits EOF tokens when configured.

## State And Persistence Behavior
Lexer state is in-memory and mutable: `lexpos`, `lineno`, active state, state stack, and current input change during scanning. Optimized mode may persist generated lexer tables to a Python module under `outputdir` or the caller package; `readtab()` reloads those tables and rebinds functions from a dictionary. `clone()` shallow-copies the lexer and can rebind rule methods to another object, so compiled regexes are shared while state cursors become independent.

## Dependencies And Integration Points
The module depends on Python `re`, `sys`, `types`, `copy`, `os`, and `inspect`. It is imported by `refparser.py`, which defines sepolgen's token rules and calls `lex.lex()` from parser global initialization. The API mirrors upstream PLY, so yacc integration expects `token()` and `input()` semantics and `tok.lexer` callbacks.

## Risks And Edge Cases
Regex rules that match empty strings, duplicate `t_` definitions, unspecified token names, missing `t_error`, invalid state specs, and bad literal specs are detected during validation. Optimized table loading trusts cached modules and bypasses validation, so stale tables can hide rule problems until import/version mismatch. `token()` is performance-sensitive and mutates shared lexer attributes while rule functions can also change `lexpos` or state. Cached table writing imports package modules dynamically and can fail on read-only paths. Some Python 2 compatibility branches remain, increasing maintenance complexity.

## Test Signals
Useful tests build lexers from function and string rules, exercise inclusive/exclusive states, ignored tokens, literals, error callbacks that do and do not advance `lexpos`, EOF callbacks, optimized lextab write/read, object-bound cloning, duplicate-rule diagnostics, and unknown token returns. Parser-level tests in `refparser.py` also validate this module indirectly by scanning real `.if`, `.te`, and `.spt` policy text.
