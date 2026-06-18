<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/rand.go -->
# sources/storage-engines/pebble/internal/randvar/rand.go

Purpose: small RNG helpers for the `randvar` package.

Important APIs/functions: `NewRand` and `ensureRand`.

Control flow and state: `NewRand` constructs a new `math/rand/v2.Rand` using a PCG source seeded with zero stream and a random `rand.Uint64()` seed. `ensureRand` returns its argument when non-nil or a new random generator otherwise.

Persistence and integration: state is caller-owned RNG state. This helper is used by `Deck` and skewed-latest tests. Risks include non-reproducibility when callers pass nil, no way to inject deterministic seed through `NewRand`, and shared RNG thread-safety depending on caller usage. Tests indirectly exercise it through randvar generators.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/rand.go -->
