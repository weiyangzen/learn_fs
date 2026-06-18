# sources/test-tools/syzkaller/tools/syz-headerparser/test_headers/th_a.h

Purpose: fixture header for the legacy Python header parser, focused on struct references, pointer typing, comments, bool fields, and unknown typedef-like names.

Important APIs and flow: header guard wraps macros and `struct A`, whose fields include `struct B* B_item`, `const char* char_ptr`, `unsigned int an_unsigned_int`, two bools, and `some_type var`.

State and persistence: declarations only.

Dependencies and integration: intended to be parsed alongside `th_b.h`, which defines `struct B` and enum/union fixtures. Comments exercise preprocessing and parser tolerance.

Risks: `some_type` is intentionally unresolved and may pass through as a native type string. `const char*` handling depends on pycparser and type formatting.

Test signals: confirms `GlobalHierarchy` can link `struct B*`, map char pointers, and preserve unknown types in metadata output.
