# sources/sync-backup/restic/cmd/restic/cmd_ls.go

Purpose: implements `restic ls`, listing files in a snapshot with text, JSON lines, or ncdu export output, optional path filters, recursion, and sorting.

Important APIs/types/functions: `LsOptions`; `lsPrinter` interface; `jsonLsPrinter`; `ncduLsPrinter`; `textLsPrinter`; `runLs`; `sortedPrinter`; `SortMode`. `lsNodeJSON` and `lsNcduNode` serialize nodes for machine formats.

Control flow and state: `runLs` validates snapshot argument, incompatible `--json/--ncdu/--sort/--reverse` combinations, and absolute path filters. It opens a read lock, memoizes snapshots, loads the index, selects an output printer, optionally wraps it in `sortedPrinter`, resolves latest/snapshot/subfolder with `SnapshotFilter.FindLatest`, then walks the tree. Two path predicates decide whether a node is inside requested dirs or on the path toward them; walker skips irrelevant directories. No repository mutation occurs.

Dependencies and integration points: uses `data.FindTreeDirectory`, `walker.Walk`, `fs.HasPathPrefix`, `formatNode`, global terminal/JSON mode, and restic snapshot filtering. Ncdu output follows ncdu JSON format.

Risks: sorted output collects all printed nodes in memory. Path filter semantics are absolute and slash-based. Prefix-directory callbacks are suppressed in JSON and sorted modes. Ncdu nesting relies on balanced `Node`/`LeaveDir` calls.

Test signals: integration tests cover ncdu validity, sort modes, and JSON lines; unit tests cover JSON/ncdu node serialization and ncdu tree formatting.
