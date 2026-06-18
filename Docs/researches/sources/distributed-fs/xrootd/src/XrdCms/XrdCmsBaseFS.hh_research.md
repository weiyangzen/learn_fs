# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsBaseFS.hh

## Purpose
Declares the base filesystem lookup engine and its queued request record type for CMS file-location decisions.

## Important APIs, Types, and Functions
`XrdCmsBaseFR` stores route masks, request stream/modifier, path buffer, path length, and parent-directory position. `XrdCmsBaseFS` exposes `Exists()` overloads, `Init()`, `Limit()`, `Pacer()`, `Runner()`, `Start()`, retry setters/getters, and flags such as `Cntrl`, `DFSys`, `Immed`, and `Servr`.

## Control Flow
The header defines the contracts used by routing code: existence can return online, pending, unknown queued, or missing. Queue state is split into paced and runnable lists and consumed by background threads.

## State and Persistence Behavior
State includes callback pointer, directory hash cache, queue semaphores/lists/counters, retry counts, cache lifetimes, and mode flags. `XrdCmsBaseFR` may steal the request buffer from `XrdCmsRRData` and frees it in its destructor.

## Dependencies and Integration Points
Includes CMS path/list/request/types, generic hash, and pthread primitives. Exposes global `XrdCms::baseFS` for cluster components.

## Risks and Edge Cases
Ownership differs between the two `XrdCmsBaseFR` constructors, so misuse can lead to leaks or double frees. The callback pointer is raw and must outlive the baseFS object. Queue semantics depend on signed `PDirLen` encoding.

## Test Signals
Compile tests should catch struct/protocol field drift. Unit tests should cover `XrdCmsBaseFR` ownership behavior, `Init()` flag combinations, `Limit()` calculations, and retry defaults.
