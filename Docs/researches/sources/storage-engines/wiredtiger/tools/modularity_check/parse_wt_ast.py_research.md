# sources/storage-engines/wiredtiger/tools/modularity_check/parse_wt_ast.py

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/parse_wt_ast.py -->
## sources/storage-engines/wiredtiger/tools/modularity_check/parse_wt_ast.py

### Purpose
`parse_wt_ast.py` parses WiredTiger C and header files with tree-sitter to extract module-level functions, macro functions, structs, typedefs, field accesses, function calls, and type uses for dependency analysis.

### Important APIs, Types, and Functions
Dataclasses `Struct`, `Function`, and `File` carry parsed metadata. `descendants_with_name` recursively collects AST nodes. `parse_struct`, `parse_typedef_struct`, `parse_function`, `parse_macro_funcs`, `parse_funcs`, and `parse_types` extract symbols and uses. `preprocess_file` rewrites problematic WT macros/attributes before parsing. `file_path_to_module_and_file` maps `../../src/...` paths to module names with special handling for checksum, OS folders, and include headers. `source_files` reads `dist/filelist` and `dist/extlist`; `parse_wiredtiger_files` filters source files and uses multiprocessing by default.

### Control Flow
The module initializes a C tree-sitter parser at import. Parsing reads and preprocesses each file, parses to an AST, and builds a `File` object by combining parsed functions/macros and type definitions. In non-debug mode, `parse_wiredtiger_files` maps `process_file` across a multiprocessing pool.

### State and Persistence
No persistent output is written. Runtime state includes parser objects and parsed-file lists. Multiprocessing workers return dataclass objects to the parent process.

### Dependencies and Integration Points
Depends on `tree_sitter`, `tree_sitter_c`, multiprocessing, regex/glob/os, and `header_mappings`. Output feeds `build_dependency_graph`.

### Risks and Test Signals
Parsing is approximate: macro bodies are not fully analyzed, field access is inferred by identifier only, common call filtering is heuristic, and preprocessing may miss new macros. Assertions enforce assumptions about source shape, e.g. checksum subfolders and unique struct definitions. Tests should parse small C fixtures covering typedef structs, function pointers, macros, include-header mapping, skipped externs, WT packed/cache-line macros, and duplicate functions under conditional branches.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/parse_wt_ast.py -->
