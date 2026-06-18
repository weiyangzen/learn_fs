# sources/storage-engines/raft-engine/src/config.rs

## Purpose
Defines raft-engine runtime configuration, recovery modes, defaults, validation, and derived capacities for log recycling and prefill.

## Important APIs, Types, And Functions
Exports `RecoveryMode` and `Config`. `Config::default` sets directory, recovery, compression, format, target size, purge thresholds, memory limit, recycle, and prefill defaults. `Config::sanitize` validates and normalizes values. `recycle_capacity` and `prefill_capacity` calculate file counts from thresholds and format support.

## Control Flow
`sanitize` rejects `purge_threshold < target_file_size`, fills `purge_rewrite_threshold`, warns on deprecated `bytes_per_sync`, raises too-small recovery read block and thread counts, rejects log recycling for unsigned format versions, rejects prefill when recycling is disabled, clears ignored prefill limits, fills missing prefill limits, and warns if `memory_limit` is set without the `swap` feature.

## State And Persistence Behavior
Configuration controls on-disk format version, recovery tolerance, file size rotation, purge/rewrite thresholds, compression, and file recycling. `format_version` and recycle options are especially persistence-sensitive because unsigned V1 files cannot be safely recycled.

## Dependencies And Integration Points
Integrates with `pipe_log::Version`, serde/TOML, logging, `ReadableSize`, engine open, file pipe log builder, purge manager, and feature-gated swap support.

## Risks And Edge Cases
Misconfigured thresholds can disable purge or force excessive rewrites. Enabling recycle on unsupported formats is rejected because stale data in recycled files could be replayed. Backward-compatible spelling for tail-corruption mode must be preserved for old configs.

## Test Signals
Tests cover serde round trips, custom TOML loading, hard and soft sanitization errors, backward compatibility for recovery-mode spelling, and prefill/recycle interactions.
