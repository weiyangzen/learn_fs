<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/fsbench.go -->
# sources/storage-engines/pebble/cmd/pebble/fsbench.go

## Purpose
Defines the `pebble bench fs <dir>` Cobra command for running named filesystem benchmarks from the `bench` package.

## Important APIs, Types, and Functions
`fsBenchConfig` starts with `NumTimes: 1` and `FS: vfs.Default`. `fsBenchCmd` declares usage, help text, argument validation, and `RunE`. `init` binds `--max-ops`, required `--bench-name`, `--num-times`, and adds `listFsBench`. `runFsBench` copies `commonCfg.Verbose` into the filesystem benchmark config and delegates to `bench.RunFsBench`.

## Control Flow
Cobra parses flags, requires one directory argument and a benchmark name, then `runFsBench` invokes the benchmark runner with the shared common config and command-specific config.

## State and Persistence Behavior
The command may create or mutate files under the supplied benchmark directory according to the selected benchmark. This file only stores process-global config populated by flags.

## Dependencies and Integration Points
Depends on `bench.FsBenchConfig`, `bench.RunFsBench`, `vfs.Default`, Cobra, and `commonCfg` from `main.go`. It integrates with `fsbenchlist.go` through the nested `list` subcommand.

## Risks and Edge Cases
Config is global, so repeated in-process command execution could retain mutated fields. `MarkFlagRequired` errors are ignored, though Cobra usually records the requirement. Resource exhaustion is controlled by the benchmark implementation and user flags.

## Test Signals
No direct tests in this file. Useful signals are Cobra parsing, required flag enforcement, and `bench.RunFsBench` receiving expected directory/config values.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/fsbench.go -->
