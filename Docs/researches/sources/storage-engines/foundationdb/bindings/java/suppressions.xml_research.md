# sources/storage-engines/foundationdb/bindings/java/suppressions.xml

Purpose: Checkstyle suppression configuration for generated Java binding files.

Important APIs and flow: XML declares the Checkstyle suppressions DTD and suppresses all checks for files matching generated option and enum/error classes: `Options.java`, `ConflictRangeType.java`, `FDBException.java`, `MutationType.java`, and `StreamingMode.java`.

State and persistence: no runtime state; it affects static analysis behavior. Integration is with Java Checkstyle tooling in the binding build. Risks include regexes that are broad enough to match unintended generated-looking paths, stale generated file names, or hiding style issues if hand-written files match. Test signal is style-check stability for generated code while keeping hand-written sources checked.
