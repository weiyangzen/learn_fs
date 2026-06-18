# sources/storage-engines/foundationdb/flow/include/flow/CodeProbe.h

Purpose: defines FoundationDB code coverage probes, annotations, registration, tracing, and the `CODE_PROBE` macro.

Important APIs/types/functions: namespace `probe`; enums `AnnotationType`, `ExecutionContext`; context annotations `net2`, `sim2`; assertion annotations `NoSim`, `SimOnly` and boolean combinators; decoration `Rare`; functional `Deduplicate`; template `CodeProbeAnnotations`; interface `ICodeProbe`; template `CodeProbeImpl`; `registerProbe`, `functionNameFromInnerType`, and `CODE_PROBE` macro stack.

Control flow: `CODE_PROBE(condition, comment, annotations...)` defines compile-time string wrapper types, and when condition is true, obtains a singleton `CodeProbeImpl` and calls `hit()`. First hit traces covered state; annotations may assert context, suppress tracing, decorate trace events, or mark deduplication/context expectations.

State/persistence: each probe singleton owns atomic hit count and annotations. Registered probes form global coverage inventory in implementation files. Trace events persist coverage signals externally.

Dependencies/integration: Flow knobs and trace system; coveragetool scans `CODE_PROBE`/related macros. Used in simulation coverage reporting.

Risks: macro-generated types depend on line numbers and `COMPILATION_UNIT`. Assertion annotations can abort if probes fire in unexpected contexts. Static registration order must be handled safely by implementation.

Test signals: `printProbesXML/JSON`, missed-probe tracing, coveragetool output, and simulation/Joshua coverage runs.
