<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/replay.go -->
# sources/storage-engines/pebble/cmd/pebble/replay.go

## Purpose
Defines `pebble bench replay <workload>`, a wrapper around captured write-workload replay support in the `bench` package.

## Important APIs, Types, and Functions
`initReplayCmd` creates a default replay config, returns a Cobra command, and binds flags for count, workload name, pacer, max writes, options string, run directory, cache size, log streaming, checkpoint ignoring, and checkpoint directory.

## Control Flow
At command execution, Cobra validates exactly one workload argument and calls `c.RunReplay(cmd.OutOrStdout(), commonCfg.Verbose, args[0])`.

## State and Persistence Behavior
This wrapper only mutates the replay config from flags. Replay itself may create a run directory, use checkpoints, open Pebble DBs, write data, and stream logs depending on config.

## Dependencies and Integration Points
Depends on `bench.DefaultReplayConfig`, replay pacer implementations, Cobra, and shared `commonCfg.Verbose`. It is installed under `bench` from `main.go`.

## Risks and Edge Cases
The closure captures a single config instance, so repeated command execution in-process may retain mutations. `OptionsString` accepts whitespace-delimited OPTIONS overrides, which can be user-error-prone. Checkpoint flags can change replay starting state substantially.

## Test Signals
No direct tests here. Signals include flag parsing, pacer selection, respecting max writes, and replay command output through `cmd.OutOrStdout`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/replay.go -->
