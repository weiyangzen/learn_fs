# sources/distributed-fs/xrootd/src/XrdVoms/XrdVomsHttp.cc

Purpose: Implements the HTTP security extractor plugin entry point that populates XrdSecEntity VOMS information from an HTTPS client certificate.

Important APIs/types/functions: Local class XrdVomsHttp derives from XrdHttpSecXtractor and implements GetSecData(), Init(), InitSSL(), and FreeSSL(). XrdHttpGetSecXtractor() is the exported factory. XrdVERSIONINFO(XrdHttpGetSecXtractor, XrdVomsHttp) emits plugin version metadata.

Control flow: The factory creates XrdVomsFun, initializes it from parms, forces gCertX509 because HTTP passes OpenSSL certificate objects, and returns a new XrdVomsHttp. GetSecData() ignores unverified TLS sessions by returning success with no entity, obtains peer cert and chain from SSL, points sec.creds to a Voms_x509_in_t stack object, calls VOMSFun(), sets sec.prot to gsi on success, frees the peer cert, clears sec.creds, and returns the VOMSFun result.

State/persistence: The extractor owns a reference to an XrdVomsFun allocated by the factory. No durable state.

Dependencies/integration: Depends on XrdHttpSecXtractor API, XrdSecEntity, OpenSSL SSL/X509, XrdVomsFun, XrdVoms.hh, and version macros.

Risks: The factory allocates XrdVomsFun and passes it by reference without visible destructor cleanup in XrdVomsHttp. Returning success on unverified SSL intentionally leaves no VOMS identity but may be surprising. sec.creds points to a stack object only during VOMSFun().

Test signals: Plugin load/version tests, verified cert with VOMS attributes, unverified cert behavior, missing peer cert, VOMSInit failure, and memory leak checks around plugin unload if supported.
