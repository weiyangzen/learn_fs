# sources/storage-engines/foundationdb/contrib/lint.py

## Purpose
`lint.py` checks FoundationDB Flow/C++-like source files for `wait` calls inside `when` clauses, a pattern that can block a `choose` loop from reacting to other events.

## Important APIs, Types, And Functions
CLI setup is in `_setup_args`; logging in `_setup_logger`. `LinterIssue` formats findings. `Token` normalizes clang token location, kind, and spelling. `tokenizer(source_file_path, clang_args)` parses a file with libclang and yields tokens. `_ScopeLinter` maintains scope state and detects violations. `lint(source_file_path, clang_args)` returns issues. `_main` validates file paths and prints findings.

## Control Flow
The tokenizer yields tokens from clang's translation-unit cursor. `_ScopeLinter.accept` pushes scoping keywords (`loop`, `when`, `choose`) and braces onto a stack, increments `_inside_when_clause` on `when`, pops scopes on `}`, and reports a violation when a `wait` identifier is seen while inside a `when` clause and the current top of stack is `{`. `finalize` reports unclosed scope stack depth.

## State And Persistence Behavior
Linter state is in memory: a stack of tokens/`None` and a count of active `when` clauses. It prints findings to stdout and logs to stderr/stdout handlers. It does not modify source files.

## Dependencies And Integration Points
It depends on Python `clang.cindex` and a working libclang installation, plus clang arguments sufficient to parse the target files. It integrates with FoundationDB's actor/Flow code patterns through token spelling rather than full AST semantics.

## Risks And Edge Cases
The scope heuristic is lexical and can misclassify unrelated identifiers named `when`, `choose`, `loop`, or `wait`. `_exit_scope` sometimes returns `None` implicitly after successful pops. `_main` passes `args.clang_args` directly and may pass `None` where a list is annotated. `logger.warn` is deprecated. The rule only catches waits directly inside the current when-body brace level, not necessarily nested semantics users may care about.

## Test Signals
Tests should feed token fixtures or small source files with valid/invalid `when(wait(...))` patterns, nested scopes, unmatched braces, identifiers in non-scope contexts, missing files, and clang argument handling. Expected output is one issue per forbidden wait.
