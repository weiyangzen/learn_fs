# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiTrace.hh

## Purpose
`XrdSecgsiTrace.hh` provides the trace macro layer used by GSI-related tools and protocol code. It centralizes the mapping between named trace categories and `XrdOucTrace::What` bits and compiles trace calls away when `NODEBUG` is defined.

## Important APIs, types, and functions
The header exposes macros `QTRACE(act)`, `PRINT(y)`, `TRACE(act,x)`, `NOTIFY(y)`, `DEBUG(y)`, and `EPNAME(x)`. `QTRACE` checks the global `XrdOucTrace *gsiTrace` and tests a `TRACE_<act>` bit. `PRINT` starts a trace record using the local `epname` symbol, writes to `std::cerr`, and ends the trace record. `NOTIFY` maps to `TRACE(Debug, ...)`; `DEBUG` maps to `TRACE(Authen, ...)`.

Trace bit constants are `TRACE_ALL`, `TRACE_Dump`, `TRACE_Authen`, and `TRACE_Debug`. The file declares, but does not define, `extern XrdOucTrace *gsiTrace`.

## Control flow
The macros are intended to be embedded directly in functions. `EPNAME("name")` defines a function-local static endpoint name. Calls like `DEBUG("message")` only emit output if `gsiTrace` exists and the corresponding bit is enabled. Under `NODEBUG`, all macros expand to empty forms, leaving no runtime checks or output.

## State and persistence behavior
The only state is the external process-global `gsiTrace` pointer and its `What` mask. The header does not allocate, free, or persist anything. Files using this header must define `gsiTrace`, initialize it with an `XrdOucTrace`, and attach an `XrdSysError`/logger if output is desired.

## Dependencies and integration points
The header depends on `XrdOuc/XrdOucTrace.hh` and, in debug builds, `XrdSys/XrdSysHeaders.hh` for stream support. It is used by `XrdSecgsiProxy.cc` and `XrdSecgsitest.cc` in this subset and likely by the GSI protocol plugin elsewhere. Its category names are part of the local tracing convention, so call sites must use `TRACE_` suffixes that match the defined constants.

## Risks and edge cases
The macros assume a visible local `epname` when `PRINT`, `TRACE`, `NOTIFY`, or `DEBUG` are used; call sites that forget `EPNAME()` can fail to compile in debug builds. The macros are statement-like but not wrapped in `do { } while (0)`, so they can be fragile in nested `if/else` contexts. Because tracing writes to `std::cerr`, very verbose tracing can interleave across threads unless `XrdOucTrace` serialization is sufficient.

## Test signals
Compile tests should cover both normal and `NODEBUG` builds. Runtime tests can set `gsiTrace->What` to individual bits and verify that `NOTIFY` and `DEBUG` produce output only for enabled categories. A simple GSI utility invocation with `-debug` is an integration signal that the global trace pointer and masks are wired correctly.
