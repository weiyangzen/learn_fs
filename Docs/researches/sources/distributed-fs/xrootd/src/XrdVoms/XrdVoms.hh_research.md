# sources/distributed-fs/xrootd/src/XrdVoms/XrdVoms.hh

Purpose: Defines the common VOMS input structure for passing OpenSSL certificate and chain data to the VOMS extraction function.

Important APIs/types/functions: Includes voms/voms_api.h, openssl/x509.h, and openssl/pem.h. Defines Voms_x509_in_t with X509 *cert and STACK_OF(X509) *chain for the gCertX509 input format.

Control flow: XrdVomsHttp.cc fills Voms_x509_in_t from an SSL session and points XrdSecEntity::creds at it. XrdVomsFun::VOMSFun() consumes it when gCertFmt == gCertX509.

State/persistence: No state.

Dependencies/integration: Bridges OpenSSL TLS certificate objects with libvoms extraction and XrdSecEntity population.

Risks: The struct contains borrowed pointers; callers must keep the SSL session/cert alive while VOMSFun runs and must free only owned references.

Test signals: Compile both HTTP and GSI VOMS entry points and validate VOMSFun correctly interprets STACK_OF(X509) inputs.
