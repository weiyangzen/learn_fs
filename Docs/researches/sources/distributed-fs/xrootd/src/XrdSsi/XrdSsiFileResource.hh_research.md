# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileResource.hh

Purpose: declares `XrdSsiFileResource`, a concrete `XrdSsiResource` specialized for resources opened through the SFS file/session adapter.

Important APIs/types: `Init(const char *path, XrdOucEnv &envP, bool aDNS)` populates inherited resource metadata and private security identity. Constructor initializes the base resource with an empty name and default `mySec`.

Control flow and state: private `XrdSsiEntity mySec` backs the inherited `client` pointer after initialization. The object is owned by `XrdSsiFileSess`, so providers should copy data they need beyond the request/session lifetime.

Dependencies and integration: depends on `XrdSsiEntity`, `XrdSsiResource`, and `XrdOucEnv`. It is the resource argument passed to `Service->Prepare()` and `Service->ProcessRequest()`. Risks center on borrowed identity field lifetimes and whether providers assume `client` is always non-null. Test signals should assert inherited fields after typical opaque/security inputs.
