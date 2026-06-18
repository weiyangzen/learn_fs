# sources/distributed-fs/xrootd/src/XrdCl/XrdClCopyProcess.hh

## Purpose

This header declares the public copy-process API used by `xrdcp`, `XrdClFS`, and library callers to schedule and run file-copy jobs. It also declares `CopyProgressHandler`, the progress/cancellation callback interface shared by copy implementations.

## Important APIs, types, and functions

`CopyProgressHandler` has virtual hooks `BeginJob`, `EndJob`, `JobProgress`, and `ShouldCancel`, all with default no-op behavior except `ShouldCancel`, which defaults to false.

`CopyProcess` exposes `AddJob(const PropertyList&, PropertyList*)`, `Prepare()`, and `Run(CopyProgressHandler*)`. `AddJob` accepts the property contract documented in the header: source, target, force, POSC, coerce, makedir, third-party mode, checksum settings, chunk settings, init/TPC/copy timeouts, dynamic source, configuration jobs, and result keys.

`MarkTPC(PropertyList&)` is a private helper that adds `xrdcl.intent=tpc` CGI to source and target URLs before TPC job creation.

## Control flow

Callers create a process, add jobs, add an optional configuration job, call `Prepare`, then call `Run`. Progress hooks are invoked around and during each job, and cancellation is checked during chunk transfer by concrete jobs.

## State and persistence behavior

`CopyProcess` hides its mutable state behind `CopyProcessImpl* pImpl`, keeping ABI exposure small. It does not persist state itself; jobs write destinations and fill caller-provided result property lists.

## Dependencies and integration points

The header depends on `URL`, `XRootDResponses`, `PropertyList`, `<cstdint>`, and `<vector>`. It is the main public integration point for XrdCl copy functionality, bridging CLI commands, filesystem commands, `ClassicCopyJob`, TPC fallback, and progress UI.

## Risks and edge cases

The property contract is stringly typed. Typos or mismatched types are mostly caught at runtime, and result keys must match exact spellings used by implementations. Callback implementations used with parallel jobs must be thread-safe. Because `Prepare` and `Run` are separate, callers must not mutate job properties unexpectedly between them unless they understand the lifecycle.

## Test signals

Tests should exercise the public contract through `AddJob`/`Prepare`/`Run`, including property defaults, cancellation, progress callback order, result keys, serial and parallel execution, and TPC intent marking.
