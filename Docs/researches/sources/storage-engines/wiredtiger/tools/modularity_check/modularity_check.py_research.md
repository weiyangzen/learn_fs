# sources/storage-engines/wiredtiger/tools/modularity_check/modularity_check.py

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/modularity_check.py -->
## sources/storage-engines/wiredtiger/tools/modularity_check/modularity_check.py

### Purpose
`modularity_check.py` is the command-line entry point for querying WiredTiger module dependencies and privacy characteristics.

### Important APIs, Types, and Functions
`parse_args` defines subcommands: `who_uses`, `who_is_used_by`, `list_cycles`, `explain_cycle`, `privacy_report`, and `generate_dependency_file`. `main` parses all WiredTiger files through `parse_wiredtiger_files`, builds the dependency graph, and dispatches to query functions.

### Control Flow
On execution, the script changes the current working directory to its own directory because parser paths are hard-coded relative to it. It always reparses the source tree and rebuilds the graph before executing a command. Cycle listing uses `nx.simple_cycles` with `length_bound=3` and prints cycles containing the requested module.

### State and Persistence
Most commands only print. `generate_dependency_file` writes `dep_file.new` via the query module. No cache is maintained, so every invocation recomputes.

### Dependencies and Integration Points
Depends on argparse, ast literal parsing for cycle arguments, os, NetworkX, `parse_wt_ast`, `build_dependency_graph`, and `query_dependency_graph`. It integrates the parser/build/query pipeline.

### Risks and Test Signals
Full-tree parsing can be expensive and sensitive to tree-sitter dependency availability. `explain_cycle` trusts `ast.literal_eval` input shape. Tests should cover every subcommand with a small mocked graph/parser or a known fixture source tree, including working-directory behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/modularity_check.py -->
