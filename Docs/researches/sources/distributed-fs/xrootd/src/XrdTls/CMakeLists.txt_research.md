# sources/distributed-fs/xrootd/src/XrdTls/CMakeLists.txt

Purpose: Adds the TLS support sources to the XrdUtils target.

Important APIs/types/functions: Uses target_sources(XrdUtils PRIVATE ...) to compile XrdTls.cc/.hh, XrdTlsContext.cc/.hh, hostcheck and notary inline/header helpers, XrdTlsNotary.cc/.hh, XrdTlsPeerCerts.cc/.hh, XrdTlsSocket.cc/.hh, and XrdTlsTempCA.cc/.hh.

Control flow: There is no conditional logic in this file. Inclusion in the build is inherited from the surrounding build tree that defines XrdUtils and the OpenSSL/library dependencies.

State/persistence: No runtime state.

Dependencies/integration: The file makes TLS a built-in part of XrdUtils instead of a separate module. That means downstream users of XrdUtils get the common TLS abstractions, hostname validation, peer cert wrapper, and temporary CA bundling support.

Risks: The file lists .icc helpers but does not list XrdTlsTrace.hh, likely because it is a header-only include not needed by CMake for compilation. Build correctness depends on higher-level CMake linking XrdUtils against OpenSSL and other Xrd libraries used by these sources.

Test signals: A clean CMake configure/build should compile all listed units and fail if OpenSSL symbols or XrdCrypto/XrdSys dependencies are not available through the parent target.
