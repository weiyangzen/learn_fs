# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdGStream.hh

Purpose: defines the plugin-facing interface for writing generic monitoring records into the XRootD G-Stream.

Important APIs/types/functions: `Flush`, `GetDictID`, `HasHdr`, `Insert(const char*,int)`, `Reserve`, `Insert(int)`, `SetAutoFlush`, `GetAutoFlush`, `Space`, and `MaxDataLen` (`65280`). The constructor binds the facade to an `XrdXrootdGSReal` reference.

Control flow: callers either insert a complete null-terminated record or reserve a buffer, fill it, then call `Insert(dlen)` to commit or `Insert(0)` to cancel. Dictionary mapping can be requested for paths or generic info and is automatically emitted when headers are enabled.

State and persistence behavior: the facade has no mutable storage except the implementation reference. State and monitor persistence are delegated to `XrdXrootdGSReal`.

Dependencies: C integer types and the forward declaration of `XrdXrootdGSReal`.

Integration points: this is the stable ABI passed to monitoring-capable plugins, insulating them from UDP buffer/header details.

Risks: reserve semantics lock the underlying stream until commit/cancel, so plugin misuse can starve other producers. The API requires the length to include a terminal null byte and be at least 8 bytes, which is easy to violate in small JSON/CGI snippets. `MaxDataLen` must remain compatible with the real buffer and UDP packet limits.

Test signals: null termination validation, max/min length checks, reserve cancellation, multiple plugin producers, dictionary IDs with and without headers, and manual flush behavior.
