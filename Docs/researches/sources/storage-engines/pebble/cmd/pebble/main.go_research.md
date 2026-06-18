<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/main.go -->
# sources/storage-engines/pebble/cmd/pebble/main.go

## Purpose
Assembles the `pebble` command-line tool, including benchmark commands and introspection/tool commands with Pebble, Cockroach, and test key schema support.

## Important APIs, Types, and Functions
Global `commonCfg` holds shared benchmark options; `maxOpsPerSec` parses `--rate`. `testKeysSchema` and `defaultSchema` register columnar key schemas. `main` creates `bench` and root Cobra commands, initializes replay/scan/sync/tombstone/YCSB/fs/write benchmark commands, wires `tool.New` commands, and binds shared flags.

## Control Flow
The executable disables Cobra command sorting, builds the command tree, sets the root version string to supported Pebble format versions, assigns a 1 GiB ballast in `commonCfg`, installs common flags on relevant benchmark commands, then executes the root command and exits with code 1 if Cobra returns an error.

## State and Persistence Behavior
The file manages process-global configuration and command structure. Persistence is performed by subcommands or tool commands, not directly here. The default ballast setting reserves disk emergency space for opened DBs through shared benchmark config.

## Dependencies and Integration Points
Integrates `pebble`, `bench`, `cockroachkvs`, `testkeys`, `base.DefaultComparer`, `colblk`, `tool`, and Cobra. It registers comparers, mergers, and key schemas so CLI readers can understand Cockroach and test SSTables.

## Risks and Edge Cases
Global config can carry state across multiple command executions in tests. Several commands share the same `commonCfg` and rate flag, so flag defaults and initialization order matter. The tool assumes installed schemas are sufficient for the CLI's SSTable formats.

## Test Signals
No direct tests. Signals include `pebble --version`, command tree availability, flag parsing across benchmark commands, and successful reads of Cockroach/testkey SSTables through tool commands.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/main.go -->
