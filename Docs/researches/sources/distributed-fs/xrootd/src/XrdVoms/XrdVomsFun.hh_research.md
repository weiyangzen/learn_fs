# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsFun.hh

Purpose: Declares XrdVomsFun, the configurable VOMS extraction engine used by GSI and HTTP security plugins.

Important APIs/types/functions: CertFormat enum supports gCertRaw, gCertPEM, and gCertX509. Public methods are SetCertFmt(), VOMSFun(XrdSecEntity &), VOMSInit(const char *), constructor, and destructor. Private helpers FmtExtract(), NameOneLine(), and FmtReplace() support configuration parsing and output formatting.

Control flow: Callers construct with XrdSysError, initialize from plugin parameters through VOMSInit(), optionally override cert format, then call VOMSFun() per authenticated entity.

State/persistence: Holds configuration filters/format strings and a pointer to XrdVomsMapfile. The comment notes instances are normally never deleted except HTTP.

Dependencies/integration: Depends on OpenSSL headers, XrdOucHash/String, XrdSecEntity, XrdSysError/Logger, and XrdVomsMapfile.

Risks: Object state is mutable and not obviously synchronized; sharing one instance across concurrent calls requires confirming plugin threading model. Destructor intentionally does not own m_mapfile.

Test signals: Compile consumers and test initialization idempotence, cert format overrides, and concurrent VOMSFun calls if plugin instances are shared.
