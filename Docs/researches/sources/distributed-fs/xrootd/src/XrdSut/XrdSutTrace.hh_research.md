## sources/distributed-fs/xrootd/src/XrdSut/XrdSutTrace.hh

Purpose: provides compile-time-controlled tracing macros for XrdSut code.

Important APIs/types/functions: declares external `XrdOucTrace *sutTrace`; defines `QTRACE(act)`, `PRINT(y)`, `TRACE(act,x)`, `DEBUG(y)`, and `EPNAME(x)` when `NODEBUG` is not set. In debug-enabled builds, `QTRACE` checks `sutTrace->What` against `sutTRACE_<act>` masks, and `PRINT` formats through `sutTrace->Beg(epname)`, `std::cerr`, and `sutTrace->End()`.

Control flow: callers place `EPNAME("...")` in a function and call `TRACE`/`DEBUG`; macros short-circuit when tracing is disabled or the mask is absent. In `NODEBUG` builds all macros compile away.

State and persistence: the only state is global pointer `sutTrace`, owned elsewhere, plus static function-local endpoint names emitted by `EPNAME`.

Dependencies and integration: depends on `XrdOucTrace.hh`, `XrdSutAux.hh`, and `XrdSysHeaders.hh` for iostream compatibility. It integrates with SUT diagnostic masks from `XrdSutAux.hh`.

Risks: macros rely on a visible `epname`; stream expressions are evaluated only under tracing, so side effects in trace expressions vary by build/mask. Global `sutTrace` lifetime and thread safety are external assumptions.

Test signals: build both with and without `NODEBUG`; verify mask gating, endpoint names, no evaluation when disabled, and concurrent trace formatting through the shared trace object.
