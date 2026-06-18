# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileResource.cc

Purpose: initializes an SSI resource object from an SFS open path and `XrdOucEnv`. It maps security identity and SSI CGI/user metadata into the generic `XrdSsiResource` fields used by providers.

Important APIs and control flow: `XrdSsiFileResource::Init()` obtains `XrdSecEntity` from the environment. When present, it copies the protocol ID, borrows identity pointers, optionally resolves host through `addrInfo->Name()` when authenticated DNS is enabled, and assigns credentials. It sets `client = &mySec`, stores `rName = path`, reads `ssi.user` into `rUser`, and extracts full `ssi.cgi` content from the environment string into `rInfo`.

State and persistence: state is in the inherited resource fields and private `mySec`. There is no persistence. Most security strings are borrowed; `rName`, `rUser`, and `rInfo` are owning `std::string`s.

Dependencies and integration: depends on `XrdOucEnv`, `XrdSecEntity`, `XrdNetAddrInfo`, and `XrdSsiEntity`. It is called from `XrdSsiFileSess::open()` before `Service->Prepare()`. Risks include lifetime of borrowed `XrdSecEntity` fields, DNS lookup behavior when `authDNS` is enabled, and a suspicious duplicate assignment where `mySec.role` is assigned `entP->vorg` then overwritten by `entP->role`, leaving `vorg` unset. Test signals should cover no-security opens, `ssi.user`, raw `ssi.cgi` extraction, authenticated-DNS host selection, and VO/role mapping expectations.
