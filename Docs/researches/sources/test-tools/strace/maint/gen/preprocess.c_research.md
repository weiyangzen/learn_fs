# sources/test-tools/strace/maint/gen/preprocess.c

Purpose: transforms the raw AST into a `processed_ast` organized for code generation: preprocessor statements, custom decoders, and grouped syscall variants with condition metadata.

Important APIs/types/functions: `condition_stack`, `create_statement_condition`, `strip_whitespace`, `processing_state`, `preprocess_rec`, `find_matching`, `syscall_comparator`, `group_syscall_variants`, and `preprocess`.

Control flow: recursively walks AST nodes, pushing condition strings for `#ifdef`/`#ifndef`, collecting defines/includes with current conditions, adding decoder templates, converting syscall AST nodes into flat `struct syscall` entries, then sorting by syscall name and grouping `$`-delimited variants into parent/child trees.

State and persistence behavior: allocates processed structures and condition snapshots; no file output. Maximum preprocessor nesting is 16 and maximum syscall count is 4096.

Dependencies and integration points: consumes `ast.h` nodes from the parser and produces `preprocess.h` structures for `codegen.c`.

Risks: the `invert` flag for `#ifndef` is not reflected when storing conditions; the original condition text is emitted as parsed, so correctness depends on lexer token value. Fixed maximum counts can assert or overflow if definition files grow unexpectedly.

Test signals: variant syscall names such as `prctl$...` should group under base syscalls; nested conditionals should wrap generated output in matching preprocessor blocks.
