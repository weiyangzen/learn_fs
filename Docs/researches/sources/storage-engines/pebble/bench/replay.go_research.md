# sources/storage-engines/pebble/bench/replay.go

## Purpose
`replay.go` implements benchmark replay of recorded Pebble workloads. It initializes run directories from checkpoints, parses option overrides, configures pacing, runs `replay.Runner`, emits benchmark metrics/plots, and can exec itself for repeated independent runs.

## Important APIs, Types, And Functions
`ReplayConfig` and `DefaultReplayConfig` configure the benchmark. Methods include `args`, `RunReplay`, `runOnce`, `initRunDir`, `initOptions`, `getCheckpointDir`, `parseHooks`, `ParseCustomOptions`, and `cleanUp`. Helper factories `makeComparer`, `makeMerger`, `PacerFlag.Set`, and `overwriteValueMerger` translate serialized option names.

## Control Flow
`RunReplay` validates checkpoint flags, runs once, decrements count, and uses `syscall.Exec` for additional runs. `runOnce` constructs a `replay.Runner`, initializes a temp or configured run directory, clones checkpoint files unless ignored, parses options from checkpoint and CLI string, starts and waits for the workload, closes resources, then prints benchmark strings and plots. `ParseCustomOptions` converts whitespace-delimited CLI text into newline-delimited Pebble options while preserving section headers.

## State And Persistence Behavior
The code clones checkpoint directories into run directories, may create temporary replay directories under the current working directory, and registers cleanup functions for temp runs. It reads options files from workload checkpoints and mutates `pebble.Options` before opening/running replay. Repeated runs replace the process image.

## Dependencies And Integration Points
It depends on `pebble/replay`, `vfs.Clone`, Pebble option parsing hooks, Cockroach comparer/merger names, table filter policies, OS exec/syscall, and benchmark CLI flag plumbing. `replay_test.go` covers custom option parsing.

## Risks And Edge Cases
Risks include incomplete cleanup for configured `RunDir`, process replacement via `syscall.Exec`, option-string parsing bugs around brackets/whitespace, hard-coded supported comparer/merger names, and failure when checkpoint lacks an OPTIONS file. `MaxCacheSize` silently caps parsed cache size.

## Test Signals
`replay_test.go` validates `ParseCustomOptions` for compaction settings, cache caps, and level-specific options. Full replay execution is not unit-tested here.
