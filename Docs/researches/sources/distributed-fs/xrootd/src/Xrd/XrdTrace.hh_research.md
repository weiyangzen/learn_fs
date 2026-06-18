# sources/distributed-fs/xrootd/src/Xrd/XrdTrace.hh

## Purpose

`XrdTrace.hh` defines trace flags and debug macros for Xrd server subsystems. The file was read completely.

## Important APIs, Types, and Functions

Trace masks include `TRACE_DEBUG`, `TRACE_CONN`, `TRACE_MEM`, `TRACE_NET`, `TRACE_POLL`, `TRACE_PROT`, `TRACE_SCHED`, and TLS-specific flags. When `NODEBUG` is not set, `TRACE(act,x)`, `TRACEI(act,x)`, and `TRACING(x)` expand to `XrdSysTrace` checks and `SYSTRACE()` calls. `XRD_TRACE` defaults to `XrdGlobal::XrdTrace.` unless an implementation overrides it.

## Control Flow

The macros gate debug output at runtime by checking `XRD_TRACE What` against a requested mask. With `NODEBUG`, trace macros compile to no-ops and `TRACING()` is zero.

## State and Persistence Behavior

This header owns no runtime state, but relies on the global or overridden `XrdSysTrace` object. Trace settings persist in that object for process lifetime or until configuration changes.

## Dependencies and Integration Points

It integrates with `XrdSysHeaders.hh`, `XrdSysTrace.hh`, and the `XrdGlobal::XrdTrace` singleton. Source files commonly define `TraceID` and optionally override `XRD_TRACE` before including this header.

## Risks and Edge Cases

Macro syntax depends on `XRD_TRACE` ending with a member-access token. New trace categories must avoid bit collisions, especially TLS composite bits. Code compiled with `NODEBUG` loses trace side effects entirely, so trace expressions must be side-effect free.

## Test Signals

Build tests should cover debug and `NODEBUG` configurations. Runtime tests can verify that setting trace masks enables expected scheduler/network/protocol logs without evaluating disabled trace expressions.
