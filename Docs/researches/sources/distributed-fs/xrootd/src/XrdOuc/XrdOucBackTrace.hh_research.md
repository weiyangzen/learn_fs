# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucBackTrace.hh

## Purpose
Documents and declares the public backtrace debugging interface for XRootD and general code.

## Important APIs and types
`DoBT()` produces a generic backtrace header including `thisP` and `objP`, with optional head/tail strings and a `force` flag. `Init()` configures XRootD-specific request/response filters from strings or environment variables. `Filter()` configures pointer filters. `XrdBT()` emits an XRootD-specific trace including request and response names.

`PtrType` distinguishes `isThis` and `isObject` filters. `Action` selects add, clear, delete, or replace behavior.

## State, dependencies, and integration
The header itself has no includes besides guards; implementation supplies all platform and protocol dependencies. It is designed for selective debugging of rare races or unexpected protocol paths and is safe to call from multiple threads according to the comments.

## Risks and test signals
The filtering rules are non-trivial: pointer filters can force traces, both pointer lists set can suppress nonmatching calls, and `XrdBT()` requires code filters unless forced. Tests should encode the documented filtering matrix and verify `force=true` bypasses all configured filters.
