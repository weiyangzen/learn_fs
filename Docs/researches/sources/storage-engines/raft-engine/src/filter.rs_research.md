# sources/storage-engines/raft-engine/src/filter.rs

## Purpose
`filter.rs` implements a scripting-enabled replay machine that filters existing raft-engine log files using Rhai callbacks. It replays log items, tracks a simplified per-Raft-group state, decides whether to keep or discard incoming or existing data, and rewrites affected files safely.

## Important APIs, Types, And Functions
`FilterResult` has three outcomes: default application, discard the incoming item, or discard existing state. `RaftGroupState` tracks `first_index`, total entry `count`, and `rewrite_count`; `apply` validates and updates state for entry indexes, compact commands, and clean commands.

`RhaiFilter` owns an `Arc<Engine>`, compiled `AST`, and `Scope`. `filter` dispatches to optional Rhai functions `filter_append`, `filter_compact`, and `filter_clean`, passing raft group state, queue, and incoming item details. Missing functions default to no filtering; other script errors become corruption.

`RhaiFilterMachine` implements `ReplayMachine`. It stores file-local retained items and per-group states. `replay_item` applies script decisions, marks files as filtered when items are removed or existing state is discarded, updates group state, and stores retained items. `merge` replays the right-hand machine's retained items into the left machine so global state is recomputed in order.

`finish` rewrites only filtered files. It renames each target to `.bak`, installs a `scopeguard` recovery action, reads raw entry bytes from the backup, rebuilds `LogBatch` records in about 64 KiB chunks, writes the new file with the original format, closes it, then removes backups and defuses guards. `RhaiFilterMachineFactory::from_script` compiles and validates a script, and its `Factory` implementation creates fresh machines with shared engine and AST.

## Control Flow
During recovery, batches enter `RhaiFilterMachine::replay`. A new `FileAndItems` bucket is started whenever the `FileId` changes. Each item is inspected against current state. `DiscardIncoming` drops the item and marks the current file for rewrite. `DiscardExisting` marks the file, clears the state, injects a synthetic `Compact { index: u64::MAX }` command, then applies and stores the incoming item. Default applies and stores the item.

After replay, callers invoke `finish` to persist changes. Entry-index items require reading the original entry block from the `.bak` file, decoding it, slicing out each entry by offset and length, and re-adding raw entries to a new batch. Commands and key-values are copied logically. Any failure before guard defusal attempts to restore the original `.bak` over the target.

## State And Persistence Behavior
The replay phase is in-memory and deterministic over ordered log items. Persistence changes happen only in `finish`, and only for files marked `filtered`. The rewrite preserves log file format and file name but may pack items into different physical batch boundaries. Backup files use the `.bak` extension beside the original file. The panic-on-restore-failure guard makes partial failure visible and tells operators to manually restore from backup.

The state model treats append holes or writes to compacted entries as corruption, while rewrite holes or compacted overlaps clear state. Rewrite entries must be contiguous with the current rewrite prefix.

## Dependencies And Integration Points
This module is gated by the crate's `scripting` feature. It depends on Rhai, `hashbrown`, `scopeguard`, debug file readers/writers, `ReplayMachine`, `LogBatch`, `LogItemBatch`, `EntryIndexes`, `Command`, `KeyValue`, `LogQueue`, and `Factory`. It plugs into `DualPipesBuilder::recover` as a custom replay machine, then uses debug I/O helpers to rewrite physical files.

## Risks And Edge Cases
`RhaiFilterMachineFactory::from_script` unwraps compilation and initial execution errors, so invalid scripts panic rather than returning `Result`. `FilterResult::from_i64` treats unexpected script return values as unreachable and can panic. `finish` uses `Path::exists` on backup paths directly, which bypasses the `FileSystem` abstraction for that check and removal. Rewriting changes batch layout and requires entry bytes to decode successfully from backups. The state model is intentionally simplified and may not represent every engine invariant.

## Test Signals
No tests are defined in this file. Its behavior is indirectly testable through scripting-feature recovery flows: script callback dispatch, missing callback defaults, state corruption detection, backup restoration on rewrite failure, and final engine recovery from filtered files are the important signals to cover.
