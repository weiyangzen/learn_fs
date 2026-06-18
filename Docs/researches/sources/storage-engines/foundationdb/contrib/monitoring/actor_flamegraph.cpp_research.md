# sources/storage-engines/foundationdb/contrib/monitoring/actor_flamegraph.cpp

## Purpose
This standalone C++ tool converts actor trace event files into folded stack samples suitable for flamegraph-style visualization. It reconstructs actor parent stacks and accumulates run time per stack/name path.

## Important APIs, Types, And Functions
`Actor` stores an actor id, name, inherited stack, accumulated `runTime`, and `lastStart`; its destructor calls `collect()` to add a folded stack line into shared `results`. `Traces` parses files, maintains the active `currentStack`, maps actor ids to `Actor` objects, and prints aggregate results. `usage` and `main` implement the CLI.

Input event opcodes are `OP_CREATE=0`, `OP_DESTROY=1`, `OP_ENTER=2`, and `OP_EXIT=3`. Each input line must split into four semicolon-separated fields: timestamp, op, name, id.

## Control Flow
For create events, the tool creates an actor and copies the current top actor's stack plus name as parent context. Destroy erases the actor, causing destructor aggregation. Enter creates an actor if missing, pushes it on the current stack, and records start timestamp. Exit verifies the top id, accumulates elapsed time, and pops. At end-of-file, it prints `DONE`, clears active stacks and actors, then `main` prints all folded stacks and weights.

## State And Persistence Behavior
All state is in memory: actor map, active stack, and aggregate folded-stack result map. The tool reads input trace files and writes text to stdout. It does not modify input files.

## Dependencies And Integration Points
It depends on the C++ standard library and is built by the adjacent CMake file. Output format is compatible with folded stack consumers such as flamegraph scripts, where each line is `frame;frame;leaf weight`.

## Risks And Edge Cases
The source uses `std::unordered_map::contains`, requiring C++20. It includes `<stack>` but uses `std::deque` without directly including `<deque>`, relying on transitive includes. `-h` works, but the parser treats `--` as help in one branch and as end-of-args in another depending on position. Empty file list prints an error but continues and returns success after printing empty output. Malformed lines throw nonfatal `Error`, so later files may still process. Unbalanced exits only warn and may leave timing incomplete.

## Test Signals
Tests should feed create/enter/exit/destroy traces and verify folded output weights, parent stack inheritance, repeated identical frames collapsed with `(n)`, malformed-line diagnostics, unbalanced stack warnings, missing file failure, and multi-file aggregation. Build tests should enforce C++20 or avoid `contains`.
