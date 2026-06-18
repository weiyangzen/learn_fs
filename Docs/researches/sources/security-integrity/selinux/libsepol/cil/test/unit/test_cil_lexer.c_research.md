# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_lexer.c

## Purpose
This file tests basic CIL lexer setup and token iteration. It validates that a small CIL input buffer can be initialized and that lexer output preserves token type, token value, and line number for common syntax.

## Important APIs, Types, And Functions
It includes `policydb.h`, `CuTest.h`, `test_cil_lexer.h`, and `cil_lexer.h`. The test entry points are `test_cil_lexer_setup` and `test_cil_lexer_next`. Important external APIs are `cil_lexer_setup`, `cil_lexer_next`, and `struct token` with token types `OPAREN`, `SYMBOL`, `QSTRING`, `CPAREN`, and `COMMENT`.

## Control Flow
Both tests allocate a mutable buffer with two trailing NUL bytes, copy a CIL string into it, call `cil_lexer_setup`, and assert `SEPOL_OK`. The token iteration test then repeatedly calls `cil_lexer_next` and verifies the sequence `(`, `test`, `"qstring"`, `)`, and `;comment`, all on line 1.

## State And Persistence
The lexer appears to keep input cursor state internally after setup. The tests use heap buffers and free them after token checks. There is no durable persistence. Because the lexer consumes or references the provided buffer, buffer lifetime and NUL padding are important state assumptions.

## Dependencies And Integration Points
The test is registered by `CilTest.c` and targets lexer internals directly. It is upstream of parser tests: parser behavior depends on lexer tokenization being stable for parentheses, symbols, quoted strings, comments, and line accounting.

## Risks
Coverage is minimal: it does not check EOF behavior, multi-line comments or symbols, malformed quoted strings, whitespace variety, error paths, or lexer cleanup. The test assumes comment line remains 1 even with a trailing newline after the comment, so line-number semantics beyond this simple case are not validated.

## Test Signals
Useful signals are correct setup return code, ordered tokenization of basic syntax, retention of raw token text including quotes and semicolon, and stable line number reporting for a single-line input.
