# sources/test-tools/syzkaller/pkg/codesearch/testdata/refs.c.json

Purpose: Golden codesearch database for `refs.c`.

Important APIs/types/functions: Defines functions `global_init_target`, `long_func_with_ref`, `refs0`, `refs1`, `refs2`, `refs3`, struct `global_ops`, and global variable `my_global_ops`. Records call and takes-address references plus field layout for `global_ops.prep`.

Control flow: Static expected JSON.

State and persistence behavior: Persists expected reference and definition metadata for tests.

Dependencies/integration points: Used by `FindReferences`, `DefinitionSource`, `DefinitionComment`, and `GetStructLayout` query tests.

Risks: This golden has many line-sensitive references; source edits require synchronized fixture updates. It is also important for distinguishing `calls` from `takes-address-of`.

Test signals: Strong reference-search signal, including repeated references and global initializer references.
