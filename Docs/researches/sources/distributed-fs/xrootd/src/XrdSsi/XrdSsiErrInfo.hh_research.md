# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiErrInfo.hh

Purpose: declares `XrdSsiErrInfo`, SSI's lightweight error container used by client requests, providers, and server-side prepare/response paths. It stores an error number, optional argument, and message.

Important APIs/types: `Clr()`, `Get(int &)`, `Get()`, `GetArg()`, `hasError()`, `isOK()`, and two `Set()` overloads for C strings and `std::string`. Assignment and copy construction preserve all three stored values. `Errno2Text()` is private and implemented in the `.cc` file.

Control flow and state: `Set()` uses explicit non-empty text when available; otherwise it maps `eNum` to text. `errArg` carries secondary data used by paths such as redirect/stall handling. The class owns `errText` but not any external data. It has no locking, so instances are expected to be thread-confined or externally synchronized.

Dependencies and integration: heavily used in `XrdSsiProvider`, `XrdSsiRequest`, `XrdSsiResponder`, `XrdSsiFileReq`, and `XrdSsiFileSess`. Risks include `hasError()` treating `errNum == 0` as success even when text is non-empty, and callers using `Get().c_str()` beyond the object's lifetime or after mutation. Test signals should cover copy/assignment, zero-code messages, fallback errno text, and `errArg` propagation.
