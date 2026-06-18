# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGStream.cc

Purpose: implements the public G-Stream facade by forwarding all calls to the referenced `XrdXrootdGSReal` implementation.

Important APIs/types/functions: `Flush()`, `GetDictID()`, `HasHdr()`, `Insert()` overloads, `Reserve()`, `SetAutoFlush()`, `GetAutoFlush()`, and `Space()`.

Control flow: each method delegates directly to `gStream`. The only local behavior is `SetAutoFlush()`, which converts negative values to disabled (`0`) and clamps positive values below 60 seconds up to 60 before calling the real implementation.

State and persistence behavior: no owned state beyond the reference stored in the header. Runtime side effects are whatever the real stream performs: buffer mutation, locks, scheduled flush, and monitor sends.

Dependencies: `XrdXrootdGStream.hh` and `XrdXrootdGSReal.hh`.

Integration points: this file keeps plugin-facing ABI small and hides implementation details. Plugins can receive an `XrdXrootdGStream` rather than the concrete monitor object.

Risks: all safety depends on the referenced real object outliving the facade. The auto-flush clamp only applies through the facade; internal calls to `XrdXrootdGSReal::SetAutoFlush()` bypass it.

Test signals: facade methods produce identical effects to direct implementation calls, especially auto-flush clamping, `Reserve()`/`Insert()` lock release, and invalid payload rejection.
