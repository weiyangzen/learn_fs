# sources/distributed-fs/xrootd/src/XrdCl/XrdClCheckpointOperation.hh

## Purpose

This header adds pipeline-operation wrappers for XRootD checkpoint commands and checkpointed writes. It lets higher-level code compose `Checkpoint`, `ChkptWrt`, and `ChkptWrtV` operations with the generic `FileOperation` pipeline framework used by XrdCl asynchronous operation chaining.

## Important APIs, types, and functions

`enum ChkPtCode` maps `BEGIN`, `COMMIT`, and `ROLLBACK` to `kXR_ckpBegin`, `kXR_ckpCommit`, and `kXR_ckpRollback`.

`CheckpointImpl<HasHndl>` derives from `FileOperation<CheckpointImpl, HasHndl, Resp<void>, Arg<ChkPtCode>>`. Its `RunImpl` extracts the checkpoint code, clamps the operation timeout to the pipeline timeout when smaller, and calls `file->Checkpoint(code, handler, timeout)`.

`ChkptWrtImpl<HasHndl>` wraps `file->ChkptWrt(offset, len, buffer, handler, timeout)`. `ChkptWrtVImpl<HasHndl>` wraps `file->ChkptWrtV(offset, iov, iovcnt, handler, timeout)` after copying a `std::vector<iovec>` into a stack array. Factory functions `Checkpoint`, `ChkptWrt`, and `ChkptWrtV` build timeout-configured operations from `Ctx<File>` and `Arg<>` values.

## Control flow

Users compose these operations into a pipeline. When the pipeline runs, each `RunImpl` pulls typed arguments from `this->args`, chooses the effective timeout, and dispatches the matching asynchronous private `File` method. Completion is reported through the provided `PipelineHandler`.

`XrdClZipArchive` is a visible consumer: it begins checkpoints, uses checkpointed vector writes for archive metadata/data, and commits checkpoints on close.

## State and persistence behavior

The operation objects hold a shared `Ctx<File>` wrapper and argument values. They do not persist state themselves. Persistence semantics belong to the remote server's checkpoint implementation: begin/commit/rollback and checkpointed writes are sent as file protocol operations.

## Dependencies and integration points

The header depends on `XrdClFileOperations.hh`, which supplies `FileOperation`, `Resp`, `Arg`, `Ctx`, `PipelineHandler`, and timeout mechanics. It integrates with private `File` methods, `FileStateHandler` checkpoint request construction, and ZIP archive update flows.

## Risks and edge cases

`ChkptWrtVImpl` uses `iovec iov[iovcnt]`, a variable-length array that is a compiler extension in C++ rather than standard C++. Empty vectors produce a zero-length VLA and call `ChkptWrtV` with `iovcnt == 0`, which may or may not be accepted by downstream code.

Timeout selection uses `pipelineTimeout < this->timeout ? pipelineTimeout : this->timeout`; if either value uses `0` as "no timeout", this minimum logic can unintentionally force zero. That behavior should match the rest of `FileOperation` conventions.

The buffer arguments are raw pointers. Callers must keep buffers alive until asynchronous completion. `Ctx<File>` can throw `logic_error` if unset, so factories require a valid file context before runtime.

## Test signals

No direct tests are included. Indirect signals come from `XrdClZipArchive` checkpointed archive writes and file-state-handler tests, if present elsewhere. Good tests would cover begin/write/commit ordering, rollback on failure, timeout propagation, vector write argument copying, and empty-vector behavior.
