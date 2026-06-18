<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/flag.go -->
# sources/storage-engines/pebble/internal/randvar/flag.go

Purpose: command-line flag adapters for numeric random variables and random byte generators.

Important APIs/types: regex `randVarRE`, `Flag`, `NewFlag`, `String`, `Type`, `Set`, `BytesFlag`, `NewBytesFlag`, `BytesFlag.Set`, and `BytesFlag.Bytes`.

Control flow and state: `Flag.Set` parses specs like `uniform:1-10`, `latest:1-10`, `zipf:1-10`, or a single value, constructs the matching `Static`, and stores the original spec. `BytesFlag.Set` parses `sizeSpec[/compressionRatio]`, delegates size parsing to `Flag`, and records target compression. `Bytes` draws a size, fills a unique prefix with random bytes, then repeats that prefix to reach the target size/compressibility.

Persistence and integration: used by metamorphic flags and other randomized test workloads. Dependencies include `flag`, `regexp`, `encoding/binary`, `rand/v2`, and local random-variable constructors. Risks include limited spec grammar, no validation for target compression <= 0, possible panic if callers pass nil RNG to `Bytes` because it uses `r.Uint64()` directly, and generated compression ratio being approximate. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/randvar/flag.go -->
