# sources/distributed-fs/xrootd/src/XrdPss/XrdPssTrace.hh

## Purpose

`XrdPssTrace.hh` defines the trace mask constants and debug macros for the proxy storage service. It gives PSS code a small wrapper over `XrdSysTrace` with a single debug bit and compile-time no-debug behavior.

## Important APIs, Types, And Functions

- `TRACEPSS_ALL` and `TRACEPSS_Debug` define the available PSS trace masks.
- `QTRACE(act)`, `TRACING(x)`, `DEBUGON`, `DEBUG(tid,y)`, and `EPNAME(x)` expand to `SysTrace` checks and `SYSTRACE` calls when `NODEBUG` is not defined.
- Under `NODEBUG`, tracing checks become false/no-op macros.

## Control Flow

There is no runtime control flow beyond macro expansion. Callers set `SysTrace.What` elsewhere, notably from `XrdPssConfig.cc` when `XRDDEBUG` or `pss.debug` is configured.

## State And Persistence

The header owns no state. It assumes an accessible `SysTrace` object and per-function `epname` string when debug macros are used.

## Dependencies And Integration Points

The non-`NODEBUG` path includes `XrdSys/XrdSysTrace.hh` and integrates with PSS files that use `EPNAME` and `DEBUG` for diagnostics. Configuration enables the mask.

## Risks And Edge Cases

- The `NODEBUG` `DEBUG` macro has a different parameter shape than the active macro, which can expose compile issues if used with two arguments in no-debug builds.
- Only one debug flag is defined, so adding more detailed categories requires coordinated changes to config parsing and this header.

## Test Signals

Build coverage should include debug and no-debug configurations. Runtime signal is visible `SysTrace` output after enabling `pss.debug` or `XRDDEBUG`.
