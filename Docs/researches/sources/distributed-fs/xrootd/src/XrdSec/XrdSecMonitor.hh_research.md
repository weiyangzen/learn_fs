# sources/distributed-fs/xrootd/src/XrdSec/XrdSecMonitor.hh

Purpose: Provides a tiny extension interface for attaching security-related metadata to monitoring streams through `XrdSecEntity::secMon`.

Important APIs and types: `XrdSecMonitor::WhatInfo` currently defines `TokenInfo`. `Report(WhatInfo, const char *)` is pure virtual and expects CGI-formatted null-terminated strings.

Control flow: Security or authorization code calls `Report` on the monitor object associated with the current mapped user. Implementations decide whether the info type is enabled and whether to emit it.

State and persistence: The interface has no state. Persistence depends entirely on the concrete monitor implementation and downstream monitoring pipeline.

Dependencies and integration points: Forward-linked from `XrdSecEntity` users; no includes are required. It is intended for optional observability rather than authentication decisions.

Risks: CGI-format strings are unvalidated at the interface boundary. Unknown enum values must be rejected by implementations. Raw `const char *` lifetime must cover the call.

Test signals: Implement a fake monitor and verify `TokenInfo` is accepted, invalid enum values are ignored, disabled monitoring returns false, and callers tolerate a null monitor pointer.
