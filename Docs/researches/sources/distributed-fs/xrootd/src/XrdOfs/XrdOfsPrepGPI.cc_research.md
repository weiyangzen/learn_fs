# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsPrepGPI.cc

## Purpose

This file implements the generic OFS prepare plugin, `PrepGPI`. It adapts XRootD prepare, stage, evict, cancel, and query requests to an external program configured by `ofs.preplib`, with bounded worker concurrency, optional query output capture, request queuing, and optional LFN-to-PFN translation.

## Important APIs, types, and functions

Global plugin state in `XrdOfsPrepGPIReal` stores logger, OSS pointer, scheduler, program, worker pool, query limits, option flags, admitted request mask, and buffer pool. `PrepRequest` owns argument/environment vectors and copied string storage. `PrepGRun` is an `XrdJob` runner with `Run()`, `Capture()`, `makeArgs()`, `Sched()`, and `DoIt()`. `PrepGPI` implements `XrdOfsPrepare::begin()`, `cancel()`, and `query()`, plus `Assemble()`, `ApplyN2N()`, `reqFind()`, `RetErr()`, and `Xeq()`.

The exported `XrdOfsgetPrepare()` parses parameters such as `-admit`, `-cgi`, `-debug`, `-maxfiles`, `-maxquery`, `-maxreq`, `-maxresp`, `-pfn`, and `-run`, initializes `XrdOucProg`, creates worker runners, and returns a `PrepGPI`.

## Control flow

At load time, parameters come from directive data or gathered config body. The plugin requires at least one admitted request and a runnable external program. For begin requests, OFS options choose `evict`, `stage`, or `prep`; unsupported request types return `SFS_ERROR`. `Assemble()` counts paths, enforces `maxFiles`, creates `XRDPREP_TID`, optional `XRDPREP_COLOC` and `XRDPREP_NOTIFY`, maps prepare flags to command arguments, adds request id/name, and appends paths, optionally adding CGI or translating to PFN.

`Xeq()` either schedules a free `PrepGRun` on the XRootD scheduler or appends the request to a global queue. `PrepGRun::DoIt()` drains the request queue serially through the runner object. Query requests either report queued/not queued when query is unsupported, or run synchronously through a dedicated runner after passing the `qryAllow` concurrency gate and capture output into the error response.

## State and persistence behavior

All state is runtime-only. Queued `PrepRequest` objects live in memory and are lost on process exit. The external prepare program may persist request state, but this file does not. Query response buffers may come from `XrdOucBuffPool` when configured above the normal error-info maximum.

## Dependencies and integration points

It depends on `XrdOfsPrepare`, `XrdOss`, `XrdScheduler`, `XrdOucProg`, config gathering/parsing helpers, `XrdOucBuffer`, `XrdOucTList`, `XrdSfsPrep`, security identity, and XRootD tracing/version macros. It is loaded by `XrdOfsConfigPI` via `XrdOfsgetPrepare`.

## Risks and test signals

Queue linkage in `Xeq()` assigns `rP->next = PrepRequest::Last` instead of linking from the old last to the new request, which appears suspicious and should be tested with more queued requests than workers. `Assemble()` in CGI mode assumes `pargs.oinfo` is present and aligned with paths. Query gating explicitly allows spurious wakeups to exceed the limit. Tests should cover parameter validation, admitted request masks, max file enforcement, PFN translation failure, CGI path building, scheduler queuing under saturation, cancel/query fallback behavior, query timeout, response truncation, and external program failure propagation.
