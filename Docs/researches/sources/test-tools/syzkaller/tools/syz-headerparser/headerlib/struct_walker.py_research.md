# sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/struct_walker.py

Purpose: this module traverses a pycparser AST and extracts a local hierarchy of C structs and their fields.

Important APIs and flow: `StructWalker` accepts an AST or header filenames. If needed, it builds an AST with `HeaderFilePreprocessor`. `_recursive_process_item` handles declarations, type declarations, identifiers, named and anonymous structs/unions, pointers, arrays, enums, and function pointers. `_format_item` normalizes types with pointer stars and array dimensions. `_traverse_ast` ignores anonymous top-level structs and recursively lists fields, flattening anonymous nested structs/unions into dotted identifiers. `visit_Struct` records first occurrence of each named struct and skips duplicates. `generate_local_hierarchy` visits the AST and returns a map of struct name to `(type, identifier)` tuples.

State and persistence: all state is in-memory `local_structs_hierarchy` plus logging.

Dependencies and integration: depends on pycparser `c_ast` and `HeaderFilePreprocessor`. It feeds `GlobalHierarchy`.

Risks: array dimensions are cast with `int(item_ast.dim.value)`, so expressions not reduced to integer literals can fail. Anonymous nested structs without parent names raise and are skipped. Duplicate struct names are ignored. Function pointers are generalized to `void (*)()`.

Test signals: doctext and `test_headers` cover arrays, pointers, nested anonymous structs/unions, enum fields, and struct references.
