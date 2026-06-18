# sources/storage-engines/wiredtiger/tools/modularity_check/header_mappings.py

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/header_mappings.py -->
## sources/storage-engines/wiredtiger/tools/modularity_check/header_mappings.py

### Purpose
`header_mappings.py` provides manual mapping from `src/include/*.h` headers to WiredTiger modules for the modularity checker, plus a skip list for forward-declaration/extern headers.

### Important APIs, Types, and Functions
`header_mappings` maps header filenames such as `btmem.h`, `cache_inline.h`, `transaction.h`-adjacent headers, and OS-layer headers to module names. `skip_files` lists headers that should not participate in dependency graph construction, including generated extern and public extension headers.

### Control Flow
There is no runtime control flow beyond module import. `parse_wt_ast.file_path_to_module_and_file` consults these collections when resolving include headers.

### State and Persistence
The mappings are static source data. No state is persisted.

### Dependencies and Integration Points
Imported by `parse_wt_ast.py`. The correctness of dependency graph nodes for include headers depends on this file staying in sync with WiredTiger's source tree.

### Risks and Test Signals
Missing mappings cause warnings and default to `include`, which can pollute the graph. Stale mappings can misattribute dependencies. Tests should compare current `src/include` headers against mapped/skipped lists and fail on unmapped headers that are not intentionally skipped.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/header_mappings.py -->
