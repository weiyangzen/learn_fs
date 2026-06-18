# sources/storage-engines/wiredtiger/bench/wtperf/runners/wtperf_xray.sh

## Purpose
`wtperf_xray.sh` runs a wtperf workload under LLVM XRay instrumentation and produces profiling reports, stack summaries, call graph SVG, and optionally a flame graph.

## Important APIs, Types, and Functions
There are no shell functions. Key variables are `xray_home`, output paths for account/stack/graph/flame files, `XRAY_OPTIONS`, `XRAY_BINARY`, and `FLAME_GRAPH_PATH`.

## Control Flow
The script checks for `./wtperf`, validates arguments, infers the WT home from `-h` if present, verifies the binary has an `xray_instr_map` section, creates the home directory, removes old XRay outputs, runs `./wtperf -O "$@"` with XRay enabled, locates the single `xray-log.wtperf.*`, selects `llvm-xray` or `XRAY_BINARY`, then runs `account`, `stack`, and `graph` subcommands. It pipes graph output through `unflatten` and `dot`; flame graph generation is conditional.

## State and Persistence Behavior
It writes profiling artifacts into the wtperf home: `wtperf_account.txt`, `wtperf_stack.txt`, `wtperf_graph.svg`, and optionally `wtperf_flame.svg`. It also creates/removes `xray-log.wtperf.*` in the current directory.

## Dependencies and Integration Points
It depends on a wtperf binary compiled with `-fxray-instrument`, `objdump`, LLVM XRay tools, Graphviz (`unflatten`, `dot`), optional FlameGraph, and wtperf runner configs. It assumes invocation from the directory containing `wtperf`.

## Risks and Edge Cases
`rm xray-log.wtperf.* ...` without `--` is acceptable but glob behavior can be shell-dependent; errors are redirected. Multiple XRay logs abort. Argument handling `./wtperf -O "$@"` treats the first user argument as the `-O` value and passes the rest, matching usage but sensitive to quoting. Graphviz/llvm tools may be absent.

## Test Signals
Build wtperf with XRay instrumentation, run a short config, and verify all requested output files are non-empty. Also test missing instrumentation and missing `FLAME_GRAPH_PATH` paths for clear diagnostics.
