# sources/storage-engines/wiredtiger/tools/modularity_check/query_dependency_graph.py

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/query_dependency_graph.py -->
## sources/storage-engines/wiredtiger/tools/modularity_check/query_dependency_graph.py

### Purpose
`query_dependency_graph.py` provides reporting functions over the NetworkX module dependency graph, including edge explanations, cycle explanations, privacy reports, and dependency-file generation.

### Important APIs, Types, and Functions
`print_edge` prints a graph edge's `Link` metadata. `who_uses` prints incoming dependencies for a module; `who_is_used_by` prints outgoing dependencies. `explain_cycle` validates and prints each edge in a requested cycle. `privacy_report_functions` determines which module functions are called from outside; `privacy_report_structs` determines which struct fields are externally accessed, marking ambiguous fields. `privacy_report` aggregates structs/functions for a module. `generate_dependency_file` writes non-ambiguous `caller -> callee` edges.

### Control Flow
Reports iterate sorted graph edges and parsed-file lists, pull edge metadata through `nx.get_edge_attributes`, and print human-readable details. Dependency-file generation writes a header and all non-ambiguous outgoing edges.

### State and Persistence
Most functions print only. `generate_dependency_file` persists `dep_file.new` in the current working directory.

### Dependencies and Integration Points
Depends on NetworkX, collections, typing, `parse_wt_ast` dataclasses, and `build_dependency_graph.AMBIG_NODE`. It is called by `modularity_check.py`.

### Risks and Test Signals
The `who_is_used_by` local variable is named `incoming_edges` despite using `out_edges`, a readability issue not a behavior bug. Privacy counts can divide by zero if a module has no non-ambiguous fields or functions in certain branches; current code only prints percentages when private counts are nonzero, but a module with zero totals and nonzero private count should be impossible. Tests should verify reports for graphs with no edges, ambiguous edges, cycles, and mixed private/public symbols.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/modularity_check/query_dependency_graph.py -->
