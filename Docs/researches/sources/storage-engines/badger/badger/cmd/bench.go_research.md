# sources/storage-engines/badger/badger/cmd/bench.go

Purpose: defines the `badger benchmark` parent Cobra command.

Important flow: `benchCmd` provides command metadata, and `init` registers it under `RootCmd`. Subcommands in sibling files attach read, write, and table-picking benchmarks to this parent.

State and persistence: this file has no direct persistence; it is command registration glue. Dependencies are Cobra and global `RootCmd`. Risks: the parent command has no `RunE`, so invoking it without subcommands depends on Cobra help/default behavior; subcommand initialization order relies on Go package init semantics. Test signals are CLI help output and command tree tests confirming `benchmark read`, `benchmark write`, and `benchmark picktable` are registered.
