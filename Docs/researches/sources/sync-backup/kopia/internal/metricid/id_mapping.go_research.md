# sources/sync-backup/kopia/internal/metricid/id_mapping.go

Purpose: provides compact conversion between maps keyed by well-known metric names and slices indexed by persistent numeric IDs.

Important APIs/types/functions: `Mapping`, `MapToSlice`, `SliceToMap`, `NewMapping`, and `inverse`.

Control flow: `NewMapping` stores the provided name-to-index map, builds an inverse map for positive IDs, and computes `MaxIndex`. `MapToSlice` allocates a slice of length `MaxIndex`, drops unknown or zero-index keys, and stores values at `id-1`. `SliceToMap` walks input positions and emits only positions present in `IndexToName`.

State/persistence behavior: mappings are in-memory structures, but their numeric IDs define persisted compact JSON positions for metrics. Missing IDs produce zero-value holes in slices.

Dependencies/integration: used by `metricid/metricid.go` to define stable IDs for counters and distributions.

Risks/test signals: duplicate IDs in input maps are not rejected here and would overwrite inverse entries; the separate mapping tests enforce uniqueness/consecutiveness for built-in mappings. Unknown metric names are silently dropped during map-to-slice conversion.
