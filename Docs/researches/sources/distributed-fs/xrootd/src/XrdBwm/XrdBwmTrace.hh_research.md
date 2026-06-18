# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmTrace.hh

Purpose: defines trace macros and bit flags for BWM diagnostics.

Important APIs/types/functions: external `BwmTrace`; macros `GTRACE`, `TRACES`, `FTRACE`, `XTRACE`, `ZTRACE`, `DEBUG`, `EPNAME`; flags `TRACE_ALL`, `TRACE_calls`, `TRACE_delay`, `TRACE_sched`, `TRACE_tokens`, `TRACE_debug`.

Control flow: in non-`NODEBUG` builds, macros check `BwmTrace.What` and emit prefixed messages through `XrdOucTrace`; in `NODEBUG`, they compile away.

State and persistence: trace state is the global `BwmTrace.What` mask set by env/config. No persistence.

Dependencies and integration points: used across BWM implementation and configured by `xtrace` in `XrdBwmConfig.cc`.

Risks: tracing expressions can reference local variables such as `oh`, `tident`, and `epname`, so macro use must match expected context. Debug-only code can hide compile issues in `NODEBUG` permutations.

Test signals: build with and without `NODEBUG`, trace option mapping, and representative trace output for calls/delay/sched/tokens/debug.
