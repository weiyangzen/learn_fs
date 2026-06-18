# sources/storage-engines/foundationdb/fdbserver/resolver/include/fdbserver/resolver/ResolverBug.h

Purpose: defines simulation-only resolver bug state and its bug-injector identifier.

Important APIs and types: `ResolverBug` derives from `ISimBug` and stores probabilities for ignoring too-old checks, write sets, and read sets. It also carries `bugFound`, `currentPhase`, and `cycleState` fields for coordinating simulation clients. `ResolverBugID` derives from `IBugIdentifier` and overrides `create`.

Control flow, state, and persistence: state is in-memory per bug object. It is not serialized or used in production durability paths.

Dependencies and integration: included by `ConflictSet.h`; `ConflictBatch` retrieves `SimBugInjector().get<ResolverBug>(ResolverBugID())` and uses the probabilities in conflict logic.

Risks and test signals: risks are accidental production influence if probabilities are nonzero outside simulation, and stale coordination fields. Tests should assert default probabilities are zero and targeted simulation workloads can force conflict anomalies when configured.
