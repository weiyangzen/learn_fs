# sources/storage-engines/wiredtiger/tools/modularity_check/build_dependency_graph.py

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/build_dependency_graph.py -->
## sources/storage-engines/wiredtiger/tools/modularity_check/build_dependency_graph.py

### Purpose
`build_dependency_graph.py` converts parsed WiredTiger C-file metadata into a module dependency graph. Edges record why one module depends on another through function calls, type use, or struct field access.

### Important APIs, Types, and Functions
`Link` stores counters for `func_calls`, `types_used`, and nested `struct_accesses`, with printing helpers. `incr_edge_struct_access`, `incr_edge_func_call`, and `incr_edge_type_use` create/update graph edges unless the source and destination modules are identical. `build_graph(parsed_files)` builds reverse maps from functions, structs, fields, and types to modules, then walks every parsed function to add dependency edges. `AMBIG_NODE` captures unresolved or ambiguous relationships.

### Control Flow
The function first collects reverse indexes across all files. It then creates a `networkx.DiGraph`, adds each file module, and processes field accesses, function calls, and type uses. Single-owner references resolve to the owning module; multi-owner or missing references point to the ambiguous node. Ambiguous fields are also accumulated for privacy reporting.

### State and Persistence
Graph state is in-memory. Nothing is written here; consumers such as `query_dependency_graph.generate_dependency_file` may persist graph-derived output.

### Dependencies and Integration Points
Depends on dataclasses, collections counters/defaultdicts, NetworkX, and `parse_wt_ast.File`. It is called by `modularity_check.py`.

### Risks and Test Signals
Field-to-struct inference by field name is approximate and can over-report ambiguity. Empty reverse-map lookups are treated as ambiguous edges, which can obscure parser misses. Tests should use synthetic parsed files with unique, duplicate, and missing symbols, verifying edge metadata and self-edge suppression.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/build_dependency_graph.py -->
