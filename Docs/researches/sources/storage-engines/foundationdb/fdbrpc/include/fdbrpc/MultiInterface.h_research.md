## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/MultiInterface.h

Purpose: Supplies containers for multiple RPC interfaces and probability/locality-aware selection metadata used by load balancing.

Important APIs/types/functions: `KVPair` is an ordered pair by key for description helpers. `ReferencedInterface<T>` wraps an interface and precomputes `LBDistance`. `AlternativeInfo<T>` stores a model interface, probability, cumulative probability, recent busy metric, and update time. `ModelInterface<T>` provides probabilistic selection for `basicLoadBalance()`. `MultiInterface<ReferencedInterface<T>>` stores sorted referenced alternatives and exposes `countBest()`, `get()`, `getInterface()`, `getDistance()`, `getId()`, and `hasInterface()`.

Control flow: `ModelInterface` initializes equal probabilities, then periodically calls `updateProbabilities()` based on recent process busy metrics, bounded by knobs and minimum signal thresholds. `MultiInterface` shuffles alternatives, stable-sorts by locality distance when available, and computes the number of best-distance alternatives.

State and persistence behavior: State is in-memory and reference counted. `ModelInterface` has a recurring future that updates probabilities. There is no serialization support; load functions intentionally assert false for `Reference<MultiInterface<T>>` and `Reference<ModelInterface<T>>`.

Dependencies and integration points: Depends on `FastRef`, `Locality.h`, deterministic random, and Flow knobs. `LoadBalance.actor.h` consumes `MultiInterface` for storage/read routing and `ModelInterface` for basic proxy-style balancing.

Risks: Probability updates require fresh busy metrics; stale metrics abort updates. `MultiInterface<T>` non-referenced constructor asserts false but remains for templating, so correct type wrapping matters. `bestCount` drives locality fallback; incorrect locality traits or sorting can send local requests remotely.

Test signals: Tests should cover locality sort order, `countBest()` for same/different distances, probability normalization bounds, stale busy metric behavior, balance-on-requests vs CPU metric decoding, and serialization attempts failing loudly.
