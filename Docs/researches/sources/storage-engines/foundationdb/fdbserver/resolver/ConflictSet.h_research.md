# sources/storage-engines/foundationdb/fdbserver/resolver/ConflictSet.h

Purpose: declares the opaque conflict-set API and the `ConflictBatch` wrapper used by resolver code.

Important APIs and types: `ConflictSet` is forward-declared with creation, clear, and destroy functions. `ConflictBatch` extends `ConflictBatchStatus`, accepts transactions, detects conflicts for a commit version/new oldest version, and can return too-old transaction indexes. Private members store transaction info, boundary points, combined write/read ranges, conflict status array, optional conflicting-key range map, reply arena, and simulation bug injector.

Control flow, state, and persistence: the header exposes an in-memory batch lifecycle: build from transactions, detect, then discard. Persistent resolver state is not represented here.

Dependencies and integration: depends on commit transaction encoding, core conflict status values, Flow vectors/arenas, and `ResolverBug`. It is a private include for the resolver library.

Risks and test signals: risks are ownership/lifetime of `StringRef` and `VectorRef` data, optional conflicting-key map nullability, and ensuring `detectConflicts` is called once per populated batch. Tests should exercise too-old reporting, conflicting-key reporting, empty batches, and bug injection probabilities.
