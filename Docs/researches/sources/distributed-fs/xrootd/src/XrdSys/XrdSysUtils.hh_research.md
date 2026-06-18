# sources/distributed-fs/xrootd/src/XrdSys/XrdSysUtils.hh

Purpose: declares static utility functions for process metadata and signal setup.

Important APIs/types/functions: `ExecName()`, `FmtUname()`, `GetSigNum()`, `SigBlock()`, and `SigBlock(int)`.

Control flow: callers use the class as a namespace. `SigBlock()` should be called during process startup; other methods are on-demand query helpers.

State and persistence: the header declares no state, but the implementation caches executable name and mutates signal masks/handlers.

Dependencies and integration: includes `sys/types.h` and `sys/stat.h`; implementation pulls platform APIs. Used by daemon bootstrap, diagnostics, and configuration signal handling.

Risks: the API returns raw C strings and integer snprintf results, so callers must manage buffer sizes and null checks. Signal blocking has process design implications if called late.

Test signals: compile consumers, validate buffer truncation handling, and assert expected masks after startup calls.
