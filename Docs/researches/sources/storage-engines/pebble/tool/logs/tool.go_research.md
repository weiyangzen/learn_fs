## sources/storage-engines/pebble/tool/logs/tool.go

Purpose: exposes the `logs` Cobra command subtree used by `db.go` and top-level tool wiring.

Important APIs/types/functions: `NewCmd() *cobra.Command` creates the root `logs` command and a `compactions` subcommand. The subcommand runs `runCompactionLogs` and registers `--window` with a default of ten minutes and `--long-running-limit` with a default of zero, interpreted by `runCompactionLogs` as disabled.

Control flow: command construction is static: create root, create subcommand, attach duration flags, add subcommand, return root.

State and persistence: no persistent state. Cobra flag state is held in the returned command instance.

Dependencies and integration: depends on Cobra and `time`. `db.go` attaches `logs.NewCmd()` under the DB tool command tree, while parser behavior lives in `compaction.go`.

Risks: all log functionality currently hangs off one subcommand; additional log parsers must be registered here. Defaults affect aggregation output and may alter datadriven expectations if changed.

Test signals: indirectly exercised through `compaction_test.go` parser tests and any command-level fixtures invoking `logs compactions`.
