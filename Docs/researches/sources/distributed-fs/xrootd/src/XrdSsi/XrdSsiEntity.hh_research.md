# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiEntity.hh

Purpose: defines `XrdSsiEntity`, the SSI representation of authenticated client identity passed to provider/resource code. It mirrors fields commonly available from `XrdSecEntity` while keeping SSI-facing code independent of the security package.

Important APIs/types: public fields include protocol ID `prot`, `name`, `host`, `vorg`, `role`, `grps`, `endorsements`, raw `creds` plus `credslen`, reserved integer, and `tident`. `XrdSsiPROTOIDSIZE` is 8, and the constructor copies a protocol name into the fixed field with null termination.

Control flow and state: this is a plain data holder with no methods beyond construction/destruction. It does not own the string pointers by default; callers such as `XrdSsiFileResource::Init()` point fields at data owned by security/environment objects. There is no persistence.

Dependencies and integration: used by `XrdSsiResource::client` and populated from `XrdSecEntity`. Risks are lifetime-related: most members are borrowed pointers, so provider code must not retain an `XrdSsiEntity` beyond the resource/session lifetime unless it copies data. Test signals should check protocol truncation/null termination and safe behavior when optional identity fields are null.
