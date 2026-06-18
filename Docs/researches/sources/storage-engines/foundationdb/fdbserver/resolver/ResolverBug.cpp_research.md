# sources/storage-engines/foundationdb/fdbserver/resolver/ResolverBug.cpp

Purpose: registers the resolver simulation bug payload with the generic `SimBugInjector`.

Important APIs and functions: `ResolverBugID::create` returns `std::make_shared<ResolverBug>()`.

Control flow, state, and persistence: no runtime loop or persistence. It constructs fresh in-memory bug state when the simulation bug injector requests this identifier.

Dependencies and integration: depends on the public `ResolverBug.h` definition and Flow simulation bug injection. `ConflictBatch` fetches this bug object to probabilistically ignore too-old checks, read sets, or write sets.

Risks and test signals: risk is small but important: if the identifier creates the wrong derived type, conflict-set simulation tests lose intended fault injection. Simulation tests should verify the bug object is discoverable and that `bugs->hit()` paths are reachable when probabilities are nonzero.
