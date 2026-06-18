# sources/test-tools/syzkaller/tools/syz-headerparser/test_headers/th_b.h

Purpose: companion fixture header for the Python header parser, covering enum declarations, simple structs, and anonymous unions inside structs.

Important APIs and flow: includes `<linux/types.h>`, defines `enum random_enum`, `struct B` with two unsigned long fields, and `struct struct_containing_union` with an int and anonymous union containing `char* a_char` and `struct B* B_ptr`.

State and persistence: declarations only.

Dependencies and integration: parsed with `th_a.h` to supply the referenced `struct B`. Anonymous union fields test dotted field flattening in `StructWalker`.

Risks: pycparser preprocessing must handle the Linux include or be given compatible include lines. Anonymous union flattening may skip malformed parentless cases.

Test signals: validates unsigned long mapping, enum handling, nested anonymous union traversal, and cross-header struct linking.
