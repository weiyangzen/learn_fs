# sources/test-tools/syzkaller/tools/syz-declextract/testdata/types.c.json

Purpose: this golden JSON records expected type, enum, syscall, and field-flow extraction for `types.c`.

Important structure: top-level keys are `functions`, `consts`, `enums`, `structs`, and `syscalls`. Functions include the three syscall implementations, `anon_flow`, and atomic helpers. Structs include alignment cases, anonymous struct expansions, `bitfields`, `packed_t`, recursive pairs, and empty/aligned-empty structs. Consts include enum values such as `a`, `b`, `c`, `enum_foo_*`, and `enum_bar_*`.

Control-flow and facts: `anon_flow` records argument-to-field facts for nested anonymous fields, union members, typedef fields, array elements, pointer fields, and pointer-array fields. Syscall records encode nested pointer types, `__user` tags, enum args, typedef-backed fd args, and struct pointers.

State and persistence: static cache input. It is line-, ABI-, and naming-sensitive.

Risks and test signals: high-value regression signal for struct layout parity, anonymous naming stability, bitfield layout, counted-by metadata, user annotations, and recursive type handling.
