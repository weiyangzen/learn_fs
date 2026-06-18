# sources/test-tools/syzkaller/pkg/codesearch/testdata/source0.c.json

Purpose: Golden database for `source0.c` plus included `source0.h` entities.

Important APIs/types/functions: Captures functions `close`, `field_refs`, `func_accepting_a_struct`, `func_in_header`, `function_with_comment_in_header`, `function_with_quotes_in_type`, `open`, `reference_to_header_static`; structs `another_struct`, `some_struct`, `some_struct_with_a_comment`, `struct_in_c_file`; union `some_union`; enum `some_enum`; typedefs `another_struct_t`, `some_enum_t`, `some_struct_t`, and `typedefed_struct_t`.

Control flow: Static JSON only, but references encode calls, type uses, field reads/writes, and field address-taking from the C source.

State and persistence behavior: Persists expected clangtool output, including body/comment ranges, static flags, field offsets/sizes, and references.

Dependencies/integration points: Used by all codesearch command tests and merged test database creation.

Risks: Large golden file is sensitive to clang AST extraction changes, target ABI field layout, and fixture line edits. It also tests quoted attributes in type strings.

Test signals: High-value fixture for entity lookup, struct layout, comment lookup, context-aware duplicate symbol resolution, and field reference classification.
