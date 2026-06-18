# sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/skip_small_compaction.rs

Purpose: implements a lightweight hook that avoids executing subcompactions whose original KV payload is below a configured threshold.

Important APIs and types: `SkipSmallCompaction { size_threshold }`, constructor `new`, and its `ExecHooks::before_a_subcompaction_start` implementation.

Control flow: when a subcompaction is about to start, the hook compares `cx.subc.size` with `size_threshold`. If the size is lower, it logs the decision and calls `SubcompactionStartCtx::skip(SkipReason::NoNeedToDo)`. The execution loop then invokes `on_subcompaction_skipped` on all hooks and does not spawn the worker task.

State and persistence: no local persistence. Because it uses `NoNeedToDo`, `SaveMeta` does not add skipped subcompactions to final migration metadata; only actually executed or checkpoint-already-done work is persisted.

Dependencies and integration: depends on `ExecHooks`, `CId`, `SkipReason`, and `SubcompactionStartCtx`. It composes with other hooks through the tuple implementation in `execute/hooking.rs`.

Risks: using original KV size rather than physical compressed size is deliberate but can surprise operators comparing object sizes. Hook ordering matters when multiple hooks can call `skip`; the last write to the shared `Cell<Option<SkipReason>>` wins if multiple hooks mutate it.

Test signals: `test_filter_out_small_compactions` runs execution with this hook and verifies final persisted subcompactions all meet the threshold.
