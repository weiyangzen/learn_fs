# sources/distributed-fs/xrootd/python/src/PyXRootDCopyProcess.cc

## Purpose
This source implements the Python binding for XrdCl multi-job copy processing.

## Important APIs, Types, and Functions
`CopyProcess::Parallel` stores the requested parallel job count. `CopyProcess::AddJob` parses source/target and many copy options, fills an `XrdCl::PropertyList`, pushes a matching results list entry, updates copy retry environment settings, and adds the job. `Prepare` appends a configuration job with the parallel count and calls `process->Prepare()`. `Run` optionally wraps a Python progress handler, releases the GIL, runs the copy process, and returns `(status, results)`.

## Control Flow
Callers typically create `CopyProcess`, call `add_job` one or more times, call `parallel` if needed, then `prepare` and `run`. Defaults for chunk sizes and timeouts are pulled from `DefaultEnv`. `sourceLimit > 1` enables extended copy properties. `Run` always constructs a `CopyProgressHandler`, even if the Python handler is null.

## State and Persistence
Object state is an owned `XrdCl::CopyProcess`, a deque of `PropertyList` result records, and an integer parallel count. Persistent side effects are remote/local copy operations and global XrdCl environment updates for retry policy.

## Dependencies and Integration Points
Depends on `PyXRootDCopyProcess.hh`, `PyXRootDCopyProgressHandler.hh`, `Conversions.hh`, XrdCl copy constants, copy process, default environment, and property lists. `FileSystem::Copy` uses this binding internally for one-shot copy.

## Risks and Test Signals
`parallel` must be applied via a configuration job at prepare time; ordering comments mention segfault risk if done earlier. `AddJob` mutates global default environment for retry settings, which can affect other copies. Copy option parsing is dense and needs compatibility tests. Test signals include one-shot copy through `FileSystem.copy`, multi-job copy, parallel copy, checksum modes, third-party copy, progress callbacks, cancellation, and result property conversion.
