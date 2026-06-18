# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsTrace.hh

Purpose: Provides VOMS debug/print macros.

Important APIs/types/functions: When NODEBUG is not set, includes XrdSysLogger.hh and defines PRINT(y), DEBUG(y), and EPNAME(x). PRINT writes to std::cerr with gLogger->traceBeg()/traceEnd() and the XrdVoms prefix when gDebug is nonzero. DEBUG requires gDebug > 1. NODEBUG makes them no-ops.

Control flow: XrdVomsFun sets EPNAME in functions and uses PRINT/DEBUG through VOMSDBG/VOMSDBGSUBJ wrappers.

State/persistence: No state is owned here. Macros depend on ambient gDebug and gLogger members.

Dependencies/integration: Coupled to XrdVomsFun private member names and XrdSysLogger trace formatting.

Risks: Macro context is implicit, and printing goes directly to std::cerr while using logger trace delimiters. Debug output may include certificate subjects and VOMS attributes, so enable carefully in production.

Test signals: Build with NODEBUG and normal builds; run VOMSInit with dbg/dbg2 and verify expected log verbosity without crashes when gLogger is present.
