<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/metaflags/meta_flags.go -->
# sources/storage-engines/pebble/internal/metamorphic/metaflags/meta_flags.go

Purpose: centralizes command-line flags for metamorphic tests and translates parsed flag values into `metamorphic.RunOption` and `RunOnceOption` slices.

Important APIs/types: `CommonFlags`, `RunOnceFlags`, `RunFlags`, `KeyFormats`, `InitRunOnceFlags`, `InitAllFlags`, `RunOnceOnlyFlagNames`, `RunOnlyFlagNames`, `MakeRunOnceOptions`, `MakeRunOptions`, and `ParseCompare`. Flags cover directories, seeds, error injection, fail regexes, retention, max threads, instance count, op timeout, key format, initial state, leaktest, treesteps, filesystem forcing, runtime trace, op-count distribution, inner binary, previous ops, compare, run-dir, and reducer attempts.

Control flow and state: initialization registers flags on `flag.CommandLine`. Run-once and run flag sets share `CommonFlags`. `MakeRunOptions` validates split-version initial-state/previous-ops pairing and handles forced filesystem names. `ParseCompare` parses `root/{run1,run2}` and exits on invalid input.

Dependencies and integration: depends on `buildtags`, `randvar.Flag`, `errors`, regexp, and `pebble/metamorphic`. It is used by `meta_test.go` and `metarunner`. Risks include global flag collisions, `os.Exit` in parsing helpers, panic on unknown key format or filesystem, and flag compatibility drift when adding new modes. Test signals are mostly integration-level through metamorphic tests, not dedicated unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metamorphic/metaflags/meta_flags.go -->
