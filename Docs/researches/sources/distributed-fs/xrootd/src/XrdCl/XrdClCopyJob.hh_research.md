# sources/distributed-fs/xrootd/src/XrdCl/XrdClCopyJob.hh

## Purpose

This header declares `CopyJob`, the abstract base class for all XrdCl copy job implementations. It standardizes property/result storage, source/target URL extraction, and the virtual `Run` operation used by `CopyProcess`.

## Important APIs, types, and functions

The constructor stores pointers to a job property list and result list, stores the job id, and calls `Init()`. `Init()` reads `"source"` and `"target"` from the property list into `URL pSource` and `URL pTarget`; retry code can call it again after mutating properties.

`Run(CopyProgressHandler*)` is pure virtual. `GetProperties`, `GetResults`, `GetSource`, and `GetTarget` expose job state to orchestration, retry, monitoring, and progress code.

## Control flow

`CopyProcess::Prepare` creates concrete `CopyJob` instances after validating and normalizing properties. `QueuedCopyJob` calls `Run`, inspects the result, and may mutate properties and call `Init` before retrying.

## State and persistence behavior

`CopyJob` does not own the property or result lists; they are owned by `CopyProcess`/caller. It stores source and target URL snapshots that must be refreshed with `Init` after relevant property changes. No durable persistence exists here.

## Dependencies and integration points

The header depends on `XrdClPropertyList.hh`, which supplies `PropertyList`, `URL`, `XRootDStatus`, and `CopyProgressHandler` dependencies through surrounding includes. Concrete implementations include `ClassicCopyJob`, `ThirdPartyCopyJob`, and `TPFallBackCopyJob`.

## Risks and edge cases

The base class assumes `"source"` and `"target"` exist and have types accepted by `PropertyList::Get`; validation happens in `CopyProcess::AddJob`. Non-owning pointers mean caller lifetime must exceed job lifetime. Forgetting to call `Init` after changing source/target properties leaves stale URLs.

## Test signals

Tests should focus on `CopyProcess` creation and retry behavior rather than this base class alone: property validation, URL refresh after write recovery, and result list propagation.
