## sources/distributed-fs/xrootd/src/XrdSys/XrdSysE2T.hh

Purpose: declares the global errno-to-text helper `XrdSysE2T`.

Important APIs/types/functions: `extern const char* XrdSysE2T(int errcode);` accepts an errno-like integer and returns non-null descriptive text.

Control flow: no local control flow; callers delegate all conversion to the implementation.

State and persistence: no header-owned state. The implementation owns cached text storage.

Dependencies and integration: includes `<cerrno>` for errno constants. It is a central utility used by `XrdSysError`, `XrdSysLogger`, `XrdSysLogging`, `XrdSysPlugin`, and IO event diagnostics.

Risks: returned pointer lifetime and thread safety are implementation contracts, so alternate implementations must preserve stable storage. It intentionally does not expose buffer-based APIs like `strerror_r`.

Test signals: include in C++ translation units with varying platform headers, verify symbol linkage, and test common errno conversions through callers.
