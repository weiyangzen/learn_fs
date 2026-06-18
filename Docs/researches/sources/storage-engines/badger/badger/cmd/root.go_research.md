# sources/storage-engines/badger/badger/cmd/root.go

Purpose: defines the root `badger` Cobra command and shared directory flags.

Important flow: global `sstDir` and `vlogDir` hold persistent flag values. `RootCmd` uses `PersistentPreRunE: validateRootCmdArgs`; flags `--dir` and `--vlog-dir` are registered globally. Validation skips help commands, requires `--dir`, and defaults `vlogDir` to `sstDir` when omitted. `Execute` runs the command and exits with status 1 on error.

State and persistence: shared global state feeds all subcommands that open Badger databases. Dependencies are Cobra, OS exit behavior, and subcommand init registration. Risks: global variables make tests order-sensitive; help-command detection checks `strings.HasPrefix(cmd.Use, "help ")`, which depends on Cobra internals; commands that do not need a DB still require `--dir` unless explicitly structured as help. Test signals are CLI error behavior, help paths, default vlog-dir propagation, and subcommand flag inheritance.
