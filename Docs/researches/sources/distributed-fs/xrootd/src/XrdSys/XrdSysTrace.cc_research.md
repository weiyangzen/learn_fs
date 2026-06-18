# sources/distributed-fs/xrootd/src/XrdSys/XrdSysTrace.cc

Purpose: implements a stream-like tracing formatter that batches message fragments in an `iovec` and emits to `XrdSysLogger`, a callback, or stderr.

Important APIs/types/functions: `SetLogger()` overloads, `Beg()`, `operator<<(XrdSysTrace*)` as `End()`, overloads for bool, char, C strings, `std::string`, signed/unsigned integer widths, pointers, and `Insert(long double)`. The anonymous `ToMsgCB()` converts `iovec` payloads into callback strings.

Control flow: `Beg()` builds a prefix from optional user, instance name, endpoint, and text, locks the trace mutex, initializes the `iovec` array, and resets formatting buffers. Each insertion appends either a pointer to caller/static text or formatted bytes in `dBuff`. Sending `End()` appends a newline, writes through the selected destination, and unlocks.

State and persistence: each trace object owns its mutex, logger pointer, prefix name, formatting state, iovec array, prefix buffer, and data buffer. A single static callback pointer is process-wide. The fallback stderr logger is static in the end operator.

Dependencies and integration: depends on `XrdSysLogger`, `XrdSysFD_Dup`, `XrdSysPthread`, `sys/uio.h`, and trace macros in higher layers. It is the lower-level stream formatter for components not using `XrdOucTrace`.

Risks: message data is capped by 16 iovec entries and 256 formatted bytes; excess fragments silently drop. `operator<<(const char *)` calls `strlen()` and does not handle null. The char hex/octal code appears to have nibble/index mistakes, and `doFmt` state can persist until reset rules fire. The static callback is not protected by a mutex.

Test signals: verify prefix variants, logger/callback/stderr paths, all numeric formatting modes, truncation behavior, null handling expectations, and concurrent trace calls on one object.
