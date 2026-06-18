# sources/storage-engines/pebble/bench/replay_test.go

## Purpose
`replay_test.go` regression-tests CLI option string parsing for replay benchmarks. This matters because replay accepts compact command-line option overrides rather than normal Pebble options files.

## Important APIs, Types, And Functions
`TestParseOptionsStr` constructs `ReplayConfig` cases and compares parsed `pebble.Options.String()` output against expected options after defaults. It specifically exercises `ReplayConfig.ParseCustomOptions`.

## Control Flow
Each case allocates fresh options, parses `OptionsString`, pins `IteratorStack` to avoid invariants-build randomization, calls `EnsureDefaults`, and compares serialized options strings. Cache objects are unreferenced when allocated.

## State And Persistence Behavior
The test is in-memory only. It validates that command-line text mutates `pebble.Options` as intended, including capping cache size through `MaxCacheSize`.

## Dependencies And Integration Points
It depends on `pebble`, `manifest.NumLevels`, `require`, and option parsing hooks reachable through `ReplayConfig`.

## Risks And Edge Cases
Covered edge cases include multiple spaces, adjacent section headers, level-specific fields, old/new compaction concurrency fields, and cache-size caps. It does not test malformed strings or replay checkpoint initialization.

## Test Signals
The primary signal is exact options-string equality after defaults, which catches parsing drift in both replay code and Pebble option formatting.
