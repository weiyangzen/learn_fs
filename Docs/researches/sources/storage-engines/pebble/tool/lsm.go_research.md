## sources/storage-engines/pebble/tool/lsm.go

Purpose: implements `tool lsm <manifest>`, which converts MANIFEST version edits into a self-contained HTML/D3 visualization of LSM evolution.

Important APIs/types/functions: `lsmTableMetadata`, `lsmVersionEdit`, `lsmKey`, and `lsmState` are JSON payload structures consumed by `lsm_data.go` JavaScript. `lsmT` owns command flags, comparer, formatter, state, and key map. `newLSM` registers flags for embedding assets, pretty JSON, start/end edit, and edit count. `validateFlags` enforces compatible edit slicing. `runLSM` reads/coalesces/slices edits, builds keys and edits, then emits HTML with embedded or external CSS/JS. `readManifest` decodes `VersionEdit`s and resolves comparers. `buildKeys` deduplicates sorted boundary internal keys. `buildEdits` tracks current files by level, attaches virtual backings, records add/delete/sublevel deltas, and builds versions via `manifest.NewVersionWithFiles`. `coalesceEdits` folds edits before `start-edit` into synthetic starting state. `reason` classifies edits.

Control flow: after validation and manifest read, optional coalescing provides the starting LSM state for nonzero start edit. Edits are sliced by `end-edit`/`edit-count`, keys are assigned compact IDs, edit deltas are generated, and HTML is written to stdout.

State and persistence: no files are written by the command; output HTML contains serialized state. In-memory `currentFiles`, backing table map, and `state.Files` reconstruct visualization state without applying a full DB open.

Dependencies and integration: uses MANIFEST record decoding, `manifest.L0Organizer`, `NewVersionWithFiles`, comparers/formatters, and generated `lsmDataCSS`/`lsmDataJS`. The `go:generate` directive invokes `make_lsm_data.sh`.

Risks: slicing expression for `endEdit` depends on `startEdit` and can be subtle. `coalesceEdits` mutates the `startingEdit` pointer from the original slice. The visualization is approximate for reasons, relying on deleted tables, min-unflushed log, and sequence-number equality. `log.Fatal` in JSON formatting exits the process on marshal failure.

Test signals: `lsm_test.go` protects L0 sublevel construction when L0 files arrive out of sequence-number order.
