<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/main.go -->
# sources/storage-engines/pebble/internal/mkbench/main.go

Purpose: root command for `mkbench`, a Pebble benchmark data processing CLI. It converts nightly benchmark raw logs into cooked JSON/JS files consumed by benchmark visualizations.

Important APIs/functions: package global `rootCmd`, `init`, and `main`. `init` registers `ycsb` and `write` subcommands and preserves backward compatibility by copying the YCSB command flags and `RunE` onto the root command.

Control flow and state: process startup initializes Cobra commands, then `main` executes `rootCmd`. Errors are assumed to have already been printed by Cobra and cause exit status 1. The backward-compatible root behavior means invoking `mkbench` without a subcommand runs the YCSB parser using the same flags.

Dependencies and integration: uses `os` and `github.com/spf13/cobra`, plus local `getYCSBCommand` and `getWriteCommand`. It integrates with historical CockroachDB nightly Pebble benchmark scripts. Risks include flag-copy fragility, duplicated `getYCSBCommand` call in `init`, and future removal of root YCSB compatibility requiring call-site updates. Tests focus on parser behavior, not the Cobra root itself.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/mkbench/main.go -->
