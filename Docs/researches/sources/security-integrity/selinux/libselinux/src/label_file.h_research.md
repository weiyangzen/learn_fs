# sources/security-integrity/selinux/libselinux/src/label_file.h

Purpose: Defines the file-context backend's data model, compiled-file format constants, file-kind conversion helpers, regex simplification/compilation helpers, dynamic-array growth macro, spec insertion, and line/binary entry readers.

Important APIs/types/functions: key structures include `lookup_result`, `selabel_sub`, `regex_spec`, `literal_spec`, `spec_node`, `mmap_area`, and `saved_data`. Constants define compiled fcontext versions, `RESTORECON_PARTIAL_MATCH_DIGEST`, and `LABEL_FILE_KIND_*`. Helpers include `string_to_file_kind()`, `file_kind_to_string()`, `regex_has_meta_chars()`, `regex_simplify()`, `compare_literal_spec()`, `sort_specs()`, `compile_regex()`, `GROW_ARRAY`, `insert_spec()`, `next_entry()`, and `process_line()`.

Control flow: `process_line()` uses shared `read_spec_entries()` to parse regex, optional type, and context. `insert_spec()` determines literal vs regex, builds stem tree nodes up to `SPEC_NODE_MAX_DEPTH`, applies subset filtering, stores lookup records, validates contexts, and compiles regexes eagerly only in validating mode. `compile_regex()` anchors expressions, limits regex length to below 4096 bytes, and uses atomics plus mutex for once-only compilation.

State and persistence: the structures define all per-handle persistent state for file labeling, including mmap ownership and lazy caches.

Dependencies and integration: includes regex abstraction, callbacks, label internals, and SELinux internals; parts are exposed for fuzzing under `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`.

Risks and test signals: input parsing rejects non-ASCII and oversized entries, but regex complexity remains important. Tests should cover file-kind parsing, escaped literal simplification, unsupported escapes, array growth overflow, prefix filtering, validation failures, lazy compile races, and fuzz-visible functions.
