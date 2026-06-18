# sources/test-tools/syzkaller/pkg/codesearch/testdata/refs.c

Purpose: C fixture for function references, address-taking, repeated references, struct fields, global arrays, and initializer references.

Important APIs/types/functions: Defines `refs0`, `refs1`, `refs2`, `refs3`, `long_func_with_ref`, `struct global_ops`, `global_init_target`, and global variable `my_global_ops`.

Control flow: `refs3` calls `refs2(refs1, refs0())` and takes the address of `refs2`. `long_func_with_ref` repeatedly calls `refs0`, `refs1`, and `refs2`. `my_global_ops` initializes function pointer field `prep` with `global_init_target`.

State and persistence behavior: Source definitions and initializer references are persisted in `refs.c.json`. No runtime persistence.

Dependencies/integration points: Exercises `FindReferences` output limits/context snippets, function address taking, global variable references, and struct field layout.

Risks: Repeated references intentionally stress output limits; changing line counts or adding references alters golden query expectations.

Test signals: Golden JSON includes body ranges, comments, refs, field layout for `global_ops`, and references from `my_global_ops`.
