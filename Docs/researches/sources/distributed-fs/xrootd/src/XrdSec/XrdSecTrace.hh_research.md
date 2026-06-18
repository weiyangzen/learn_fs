# sources/distributed-fs/xrootd/src/XrdSec/XrdSecTrace.hh

Purpose: Defines trace bit masks for the XrdSec subsystem.

Important APIs and types: Includes `XrdOucTrace.hh` and defines `TRACE_Authenxx`, `TRACE_Authen`, and `TRACE_Debug`.

Control flow: Server configuration uses these masks in `sec.trace` parsing; runtime code checks `QTRACE(Debug)` and authentication trace categories.

State and persistence: No state. Values are compile-time constants.

Dependencies and integration points: Integrated with `XrdOucTrace` and `XrdSecServer` tracing setup.

Risks: Mask values must remain compatible with existing trace usage. The `TRACE_Authenxx` aggregate masks both auth and debug bits, so changes can affect clearing behavior.

Test signals: Parse `sec.trace all`, `debug`, `auth`, `authentication`, `off`, and negative options; verify `PManager` debug toggling follows trace state.
