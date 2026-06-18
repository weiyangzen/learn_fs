<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/randvar.go -->
# sources/storage-engines/pebble/internal/randvar/randvar.go

Purpose: declares common interfaces for random variable implementations.

Important APIs/types: `Static` exposes `Uint64(*rand.Rand) uint64`; `StaticBytes` exposes `Bytes(*rand.Rand, []byte) []byte`; `Dynamic` embeds `Static` and adds `IncMax` and `Max`.

Control flow and state: no executable logic. These interfaces define contracts used by flags, metamorphic operation counts, byte generators, Zipf/uniform/skewed-latest generators, and dynamic workloads.

Persistence and integration: interface-only; no persistence. Risks are contract ambiguity around nil RNG handling, thread-safety, inclusivity of bounds, and whether returned byte buffers may alias input buffers. Implementations in this subset vary: `Deck` tolerates nil RNG through `ensureRand`, while `BytesFlag.Bytes` expects non-nil.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/randvar.go -->
