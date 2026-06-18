# sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/checkpoint.rs

## Purpose
Implements an execution hook that skips subcompactions already recorded in checkpoint metadata under the compaction metadata output directory.

## APIs and control flow
`Checkpoint` owns a `HashSet<CheckpointedSubcompaction>`. `load` reads existing checkpointed subcompactions from external storage and extends the set while logging elapsed time. As an `ExecHooks` implementor, `before_execution_started` computes `"{out_prefix}/metas"` using `META_OUT_REL` and loads checkpoints. `before_a_subcompaction_start` converts the pending subcompaction into a checkpoint key; if present, it logs and calls `cx.skip(SkipReason::AlreadyDone)`.

## State, dependencies, and integration
State is in-memory per execution run, sourced from persisted checkpoint metadata in external storage. The hook depends on `ExternalStorage`, checkpoint save/load helpers, compaction `META_OUT_REL`, execution hook contexts, TiKV logging, and timing utilities. It integrates with the executor scheduler through the `ExecHooks` trait.

## Risks and test signals
Correctness depends on `CheckpointedSubcompaction::from_subcompaction` matching the format written by the save-meta path. Loading uses `extend`, so repeated calls accumulate rather than reset. If checkpoint metadata is stale or corrupt, valid work may be skipped or load may fail before execution. No local tests are present in this file; validation is likely covered by broader execution-hook or checkpoint integration tests.
