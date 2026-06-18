# sources/test-tools/syzkaller/tools/syz-headerparser/headerlib/container.py

Purpose: this legacy Python module converts struct field hierarchies from parsed headers into syzkaller-style metadata structs.

Important APIs and flow: `StructRepr` holds one struct name and a list of `FieldRepr` objects, formats fields with `get_syzkaller_field_body`, and maps native C types to candidate syzkaller types such as `len`, `fileoff`, `intN`, string pointers, arrays, nested structs, and enums. `FieldRepr` is a simple property container for field type, identifier, and optional linked struct metadata. `GlobalHierarchy` is a dict keyed by `"struct <name>"`; it invokes `StructWalker.generate_local_hierarchy`, converts tuples into `StructRepr`, links fields whose type references known structs, and emits sorted metadata with `get_metadata_structs`.

State and persistence: in-memory hierarchy only. Logging handlers are added per object.

Dependencies and integration: depends on `headerlib.struct_walker.StructWalker` and Python logging. Used by `headerparser.py` to print generated metadata.

Risks: type mapping is heuristic and incomplete. Logger setup can add duplicate handlers across repeated objects. `maxcolwidth` assumes at least one field, so empty structs may fail formatting. Python 2-style `object` classes and doctext indicate legacy code.

Test signals: fixture headers `th_a.h` and `th_b.h` exercise nested struct pointers, comments, bools, unknown typedefs, enums, and anonymous unions.
