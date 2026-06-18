# sources/test-tools/syzkaller/pkg/codesearch/testdata/source0.c

Purpose: Main C fixture for codesearch entity extraction across source/header boundaries, comments, duplicate names, typedef/union/struct usage, field reads/writes, static inline header calls, and compile database loading.

Important APIs/types/functions: Includes `source0.h`; defines `struct_in_c_file`, `open`, `close`, `function_with_comment_in_header`, `func_accepting_a_struct`, `function_with_quotes_in_type`, `field_refs`, and `reference_to_header_static`.

Control flow: Functions are simple, but each is structured to create specific AST references: function calls to duplicate-name symbols, casts through typedefs/unions, field reads/writes/address-taking, and a call to a static inline header function. A preprocessor guard fails compilation if `KBUILD_BASENAME` was not supplied by the test compile database.

State and persistence behavior: No runtime state; source and expected extraction are persisted through `source0.c.json`.

Dependencies/integration points: Depends on `source0.h`. Used by clangtool tests, file-index, definition/comment, reference, struct-layout, and compile_commands correctness tests.

Risks: The function named `open` can collide with common libc names conceptually, but this is intentional for extractor context. Line ranges and comments are golden-sensitive.

Test signals: Broadest C fixture in this set, validating definitions from included headers, type references, field references, comment extraction, static inline handling, and `-DKBUILD_BASENAME`.
