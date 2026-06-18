# sources/test-tools/syzkaller/pkg/codesearch/testdata/source2.c

Purpose: Duplicate-name C fixture defining a non-static `same_name_in_several_files`.

Important APIs/types/functions: Function `same_name_in_several_files`.

Control flow: Empty function body with an explanatory comment.

State and persistence behavior: Expected extracted state is in `source2.c.json`.

Dependencies/integration points: Used with `source1.c` and `source0.h` to test global versus static duplicate resolution.

Risks: Non-static duplicate resolution is weak-match fallback in `findDefinition`; fixture edits can alter query expectations.

Test signals: Golden JSON records a non-static duplicate-name function and comment range.
