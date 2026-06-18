# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucReqID.hh

Purpose: declares `XrdOucReqID`, the request ID helper used to generate per-process or per-address request identifiers and to test whether an ID belongs to the current endpoint.

Important APIs, types, and functions: public methods are `ID(char*, int)`, `isMine(char*, int&, char*, int)`, `PFX()`, and static `Index(int, const char*, int)`. Constructors support a local PID/time identity or a network-address identity. Private fields hold the mutex, prefix length, internal return offset, duplicated prefix/format strings, and sequence counter.

Control flow: users construct an instance once, repeatedly call `ID()` to fill caller buffers, use `PFX()` when a prefix is needed externally, and call `isMine()` to split local IDs from remote IDs while optionally discovering the remote hostname.

State and persistence: the class owns process-local mutable sequence state protected by `XrdSysMutex`. It stores C string pointers allocated by the implementation and does not expose copy/move control, so instances should not be copied.

Dependencies and integration points: includes platform string compatibility and `XrdSysPthread.hh`, forward-declares `XrdNetSockAddr`, and is implemented by the companion `.cc` using XrdNet and CRC utilities.

Risks and test signals: the header does not encode buffer size in the type system, and the default destructor does not free duplicated strings. Tests should focus on ABI compatibility, object lifetime expectations, concurrent use, and behavior with both constructors.
