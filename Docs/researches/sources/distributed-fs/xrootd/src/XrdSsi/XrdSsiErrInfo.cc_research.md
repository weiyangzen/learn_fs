# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiErrInfo.cc

Purpose: provides the platform/XRootD error-text conversion hook for `XrdSsiErrInfo`. It keeps errno-to-message mapping out of the header while delegating to the canonical XRootD helper.

Important APIs and control flow: the only implemented function is `XrdSsiErrInfo::Errno2Text(int ecode)`, which returns `XrdSysE2T(ecode)`. It is called by `XrdSsiErrInfo::Set()` when no explicit message is supplied or the supplied string is empty.

State and persistence: no local state, no persistence, no allocation. Dependencies are `XrdSsiErrInfo.hh` and `XrdSys/XrdSysE2T.hh`.

Integration points: used throughout SSI request/session/provider code to create stable error text for errno values. Risks are limited to the semantics of `XrdSysE2T`, especially for zero or non-errno values. Test signals should cover explicit message preservation in the header class and fallback text for representative errno values through this implementation.
