# sources/storage-engines/foundationdb/flow/CodeProbe.cpp

## Purpose
`CodeProbe.cpp` implements registration, listing, filtering, and missed-probe tracing for FoundationDB code probes used by simulation and coverage tooling.

## Important APIs, Types, and Functions
The main internal type is `CodeProbes`, a singleton containing a multimap from normalized file/line `Location` to `ICodeProbe` pointers. Public APIs in namespace `probe` include `registerProbe`, `traceMissedProbes`, `functionNameFromInnerType`, `ICodeProbe::filename`, equality operators, `printProbesXML`, and `printProbesJSON`. Annotation predicates include `probe::assert::NoSim` and `SimOnly`.

## Control Flow
Static probes register themselves into `CodeProbes::instance()`. Printing first verifies duplicate comments per file, then emits either XML coverage cases or newline-delimited JSON-like probe records, optionally filtered by execution context strings. `traceMissedProbes` coalesces probes by location, checks whether any probe at each location was hit, and traces one missed probe per unhit location when tracing is enabled.

## State and Persistence Behavior
State is process-local singleton metadata. It is not durable, but printed XML/JSON output can be consumed by external coverage tools. Probe hit state is owned by individual `ICodeProbe` instances.

## Dependencies and Integration Points
The file depends on `CodeProbe.h`, `CodeProbeUtils.h`, `Arena`, `network`, fmt, Boost demangling, and Boost unordered maps. It uses `FDB_SOURCE_DIR` to normalize file paths and `g_network` to evaluate simulation-specific annotations.

## Risks and Edge Cases
`normalizePath` uses `FDB_SOURCE_DIR` for both source and binary base variables, which may not strip true binary paths if that was intended. `printJSON` emits two demangled local type names before probe records, which looks diagnostic and may surprise machine consumers. Context parsing throws `invalid_option_value` on unknown strings.

## Test Signals
There are no unit tests in this file. Signals are generated probe lists, uniqueness warnings printed by `verify`, and missed-probe traces.
