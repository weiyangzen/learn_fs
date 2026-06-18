# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsLogin.hh

Purpose: declares the CMS login helper for admitting inbound links and initiating outbound CMS login handshakes.

Important APIs/types/functions: instance `Admit(XrdLink*, CmsLoginData&, const char *sid, const char *envP)`, static `Login(XrdLink*, CmsLoginData&, int timeout)`, constructor with optional parse buffer, and private helpers for authentication, error logging, packing/sending login data, and blacklist errors.

Control flow: inbound code constructs an `XrdCmsLogin` around a receive buffer and calls `Admit()`. Outbound code calls `Login()` with filled `CmsLoginData`. Private helpers keep wire packing and rejection logic out of connection setup code.

State and persistence behavior: object state is only the receive buffer pointer/length. Login payload fields describe persistent runtime identity such as SID, paths, environment, hold time, space, ports, and mode, but this class does not store them beyond the call.

Dependencies: `XProtocol/XPtypes.hh`, `YProtocol.hh`, `sys/uio.h`, and `XrdLink` forward declaration.

Integration points: protocol admission and manager/client connection setup rely on this class for CMS wire compatibility and authentication/blacklist behavior.

Risks: raw buffer pointers require caller-managed lifetime. `Authenticate()` is declared but implementation delegates through security helpers rather than this symbol in the current file, so declarations and definitions should be kept audited. Timeout default `-1` means blocking behavior depends on `XrdLink`.

Test signals: header/API compile tests, buffer lifetime tests around `Admit()`, outbound default-timeout behavior, and ABI checks for use from client manager code.
