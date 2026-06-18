## sources/storage-engines/pebble/sstable/block/compression_stats.go

Purpose: Collects, formats, parses, clones, aggregates, and scales per-compression-setting byte statistics for SSTables or groups of files.

Important APIs/types/functions: `CompressionStats` stores common cases inline (`noCompressionBytes`, `fastest`) and uncommon settings in a map. `CompressionStatsForSetting` tracks compressed/uncompressed bytes and computes `CompressionRatio`. `addOne`, `Add`, `All`, `String`, `Clone`, `Scale`, and `ParseCompressionStats` are the primary operations.

Control flow: `addOne` handles no-compression specially, inlines `fastestCompression`, and lazily allocates `others`. `All` yields non-empty settings. `String` builds sorted entries by algorithm and level, using compact `None:<bytes>` for no-compression and `<setting>:<compressed>/<uncompressed>` for compressed settings. `ParseCompressionStats` accepts empty strings, current `None` format, old `NoCompression:<x>/<x>` format, known settings from `compression.ParseSetting`, and accumulates unknown settings under `compression.Unknown`.

State and persistence behavior: The string form is stored in user/table properties and must remain backward-compatible. `Scale` approximates virtual table stats by multiplying by `size/backingSize` with sane lower bounds.

Dependencies and integration points: Used by `Compressor`/`PhysicalBlockMaker` to record block compression stats and by SSTable property handling. Depends on `internal/compression`, `crmath.ScaleUint64`, Go `iter`, `cmp`, `slices`, `strings`, and Pebble invariants.

Risks: `Reset` clears but does not nil the map, retaining capacity. `ParseCompressionStats` uses simple colon/comma splitting and `fmt.Sscanf`; invalid strings return generic parse errors. Unknown setting aggregation preserves total bytes but loses original algorithm names.

Test signals: `compression_stats_test.go` covers deterministic string order, accumulation, random round trips, unknown settings, and old-format parsing.
