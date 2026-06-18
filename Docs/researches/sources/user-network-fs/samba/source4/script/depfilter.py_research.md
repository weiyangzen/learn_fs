<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/depfilter.py -->
# sources/user-network-fs/samba/source4/script/depfilter.py

## Purpose

`depfilter.py` filters a Graphviz dot dependency graph to only the arcs reachable from a selected top node.

## Important APIs, Types, and Functions

The script parses one command-line argument, reads dot input from stdin, builds a `graph` mapping with a regex for `"node" -> "dep"` arcs, recursively fills `subgraph` with `add_deps(node)`, and prints a reduced dot graph.

## Control Flow

It validates argument count, stores all stdin lines, parses arcs from all lines except the first and last, recursively walks dependencies from the requested node, then emits the original graph header/footer with only reachable arcs.

## State and Persistence Behavior

All graph state is in memory. No files are written.

## Dependencies and Integration Points

It depends only on Python `sys` and `re`. It is useful with waf or build dependency graph output piped through stdin.

## Risks and Edge Cases

The regex assumes every interior line is a valid quoted arc; malformed dot input can raise `AttributeError`. Recursive traversal can hit recursion limits on very deep graphs. It does not preserve non-arc attributes.

## Test Signals

Tests should include simple chains, branching graphs, cycles, missing top node, malformed lines, and graph attributes that should be dropped or handled explicitly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/script/depfilter.py -->
