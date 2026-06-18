# sources/storage-engines/wiredtiger/tools/callgraph

## Purpose
`tools/callgraph` is a Perl analysis tool for building and querying WiredTiger C call graphs. It can render filtered Graphviz graphs, find shortest or all call paths, compute crosslink statistics, trace possible return values, grep/tag function bodies, merge DOT files, and run as an interactive server for repeated queries.

## Important APIs and modes
Major modes are `--graph`, `--path-1`, `--path-all`, `--crosslink-stats`, `--ret`, `--retl`, `--retll`, `--merge`, `--mergeflat`, and `--server`. Key helpers include argument parsing (`parseArgs`, `postProcessArgs`, `split_args`, `argv_redirect`), source loading (`read_all`), module inference (`fname_to_module`, `name_to_module`), parsing/tagging (`parse_retvals`, tag handlers), output formatting (`printPathText`, `formatNodeDot`, `printPathDot`, `pan_js`), filtering hooks (`filterEdge`, `filterNode`), graph merging, and server dispatch (`start_server`).

## Control flow and behavior
The script reads all `src`, `ext`, and optional `build` C/header files into one stream with `#line` markers, strips comments, joins selected continued lines, discovers function definitions and function-like macros, optionally records assigned function-pointer references, and scans function bodies for calls. It builds forward and reverse adjacency maps, file/module maps, return-expression maps, and tag annotations. Query modes then either traverse paths breadth/depth first with depth/prune/grow/exclude filters, emit graph nodes/edges, summarize internal/external cross-module calls, recursively expand return values, or merge preexisting DOT input.

## State, dependencies, and integration
The script uses many global hashes for graph state (`%funcs`, `%calls`, `%rcalls`, `%edges`, `%func2file`, `%func2mod`, `%funcmarks`, `%func2ret`). It depends on Perl 5.26, `Getopt::Long`, `IO::File`, Git for repo-root discovery, Unix shell commands for source collection, and Graphviz/`column` for some output modes. It is WiredTiger-specific through module aliases, function naming conventions, return macros, and cursor static initializer parsing.

## Risks and test signals
Risks include regex-based C parsing limitations, global mutable state, eval-powered custom hooks and tag substitutions, shell interpolation in source reading, temp-file/fork complexity in server mode, and output filters that depend on external tools. Signals are correct function lists for known files, plausible path results such as eviction-to-hazard examples, valid DOT/SVG/HTML output, crosslink tables, useful return-code expansion, and server commands reusing parsed source without reparsing the graph unless grep/tag metadata is requested.
