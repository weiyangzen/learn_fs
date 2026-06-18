# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiTrace.hh

## Purpose

This header defines SSI tracing masks and debug macros. It is intentionally lightweight so SSI implementation files can include it for conditional trace output without adding runtime cost in `NODEBUG` builds.

## Important APIs, types, and functions

The exported masks are `TRACESSI_ALL` and `TRACESSI_Debug`. In debug builds, `QTRACE(act)` tests `Trace.What`, `DEBUG(y)` emits `SYSTRACE` using the caller's `tident` and local `epname`, and `EPNAME(x)` declares a static endpoint name string. The header declares `extern XrdSysTrace Trace` in namespace `XrdSsi`.

## Control flow

There is no independent control flow. Callers place `EPNAME("...")` at function scope and wrap diagnostic messages with `DEBUG(...)`. The macro expands to a trace-flag check and system trace call when tracing is enabled.

## State and persistence behavior

The only state is the process-global `XrdSsi::Trace` object declared elsewhere. Trace flags are runtime configuration, not persistent state.

## Dependencies and integration points

This header depends on `XrdSys/XrdSysTrace.hh` in debug builds and integrates with files such as `XrdSsiTaskReal.cc` and `XrdSsiUtils.cc`. Its macros assume a `tident` symbol is visible in the calling method or class context, so it is coupled to SSI object's diagnostic naming convention.

## Risks and edge cases

The macro interface is fragile: missing `tident` or `epname` in a caller creates compile failures only in debug builds. Because `DEBUG(y)` evaluates stream expressions only when enabled, side effects inside debug expressions must be avoided. `NODEBUG` builds remove all debug code, so behavior must not depend on tracing side effects.

## Test signals

Build coverage should include both normal and `NODEBUG` configurations. Runtime trace tests can verify that setting `TRACESSI_Debug` emits messages and that clearing the flag suppresses them.
