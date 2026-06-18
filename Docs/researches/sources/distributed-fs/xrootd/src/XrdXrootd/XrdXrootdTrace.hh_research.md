# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdTrace.hh

## Purpose

This header defines trace bit flags and trace macros for the xroot protocol subsystem. It provides low-overhead conditional logging that compiles out under `NODEBUG`.

## Important APIs, types, and functions

Trace flags include `TRACE_DEBUG`, `TRACE_EMSG`, `TRACE_FS`, `TRACE_LOGIN`, `TRACE_MEM`, `TRACE_REQ`, `TRACE_REDIR`, `TRACE_RSP`, `TRACE_STALL`, `TRACE_AUTH`, `TRACE_FSIO`, `TRACE_FSAIO`, and `TRACE_PGCS`. Macros `TRACE`, `TRACEI`, `TRACEP`, and `TRACES` wrap `SYSTRACE` with different link/request-id contexts. `TRACING(x)` tests enabled flags.

## Control flow

Code sets a local `TraceID` and, when needed, `TRACELINK`. A macro checks `XrdXrootdTrace.What` for the requested flag and emits a structured trace message. In release/no-debug builds the macros become no-ops.

## State and persistence behavior

The header uses the external global `XrdXrootdTrace`; it persists no state itself. Trace output persistence depends on the configured XRootD logger.

## Dependencies and integration points

It depends on `XrdSysTrace` and `XrdSysHeaders` when debugging is enabled. It is included across protocol, prepare, response, transit, and execution modules.

## Risks and edge cases

Macros require caller-side identifiers such as `TraceID`, `TRACELINK`, `Response`, or `trsid` to exist for specific variants. This keeps call sites terse but makes misuse a compile-time or context error. Side effects in trace expressions are skipped when the flag is disabled.

## Test signals

Signals are mostly compile/configuration checks: all macro variants compile in representative contexts, no-debug builds remove trace dependencies, and trace flag parsing enables the expected bits.
