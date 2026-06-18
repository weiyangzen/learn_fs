# sources/storage-engines/tikv/components/compact-log-backup/src/execute/hooking.rs

Purpose: defines the hook contract for compact-log-backup execution and the context objects passed at each lifecycle point.

Important APIs and types: `ExecHooks`, `NoHooks`, `CId`, `BeforeStartCtx`, `AfterFinishCtx`, `SubcompactionStartCtx`, `SubcompactionFinishCtx`, `SubcompactionSkippedCtx`, `AbortedCtx`, and `SkipReason`. `SubcompactionStartCtx::skip` writes a skip reason into an internal `Cell`.

Control flow: execution calls `before_execution_started`, `before_a_subcompaction_start`, `after_a_subcompaction_end`, `after_execution_finished`, `on_aborted`, and `on_subcompaction_skipped` at defined points. Default trait methods are no-ops. Tuple composition runs both hooks, using `try_join` for fallible async hooks and `join` for non-fallible abort/skip hooks. `Option<T>` delegates when present.

State and persistence: no persistence; it is the in-memory extension surface. Contexts expose execution config, storage references, result metadata, runtime handles, and per-event statistics.

Dependencies and integration: used by all hook modules and by `execute/mod.rs`. It ties together `Execution`, `ExternalStorage`, `Subcompaction`, `SubcompactionResult`, and statistic deltas.

Risks: async functions in traits are allowed with a local lint exemption and do not require returned futures to be `Send`; hooks must stay compatible with how execution awaits them. Tuple hooks run fallible hook futures concurrently, so side effects can happen in both hooks even if one fails. The skip cell is mutable shared context, so hook ordering can affect the final reason.

Test signals: execution tests compose hooks such as `(SaveMeta, CompactionSpy)`, `(Blocking, StorageConsistencyGuard)`, and checkpoint/save/abort combinations, validating composition and abort semantics.
