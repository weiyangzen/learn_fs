# sources/distributed-fs/xrootd/src/XrdTls/XrdTls.hh

Purpose: Declares the common TLS facade used by XRootD TLS context and socket code.

Important APIs/types/functions: Defines enum RC with success, connection closed, missing cert/context, hostname validation failure, SSL/system/unknown/verification failures, and OpenSSL WANT states. Declares Emsg(), RC2Text(), SetMsgCB(), SetDebug() overloads, ssl2RC(), ssl2Text(), and ClearErrorQueue(). It also defines debug masks dbgOFF, dbgCTX, dbgSOK, dbgSIO, dbgALL, and dbgOUT.

Control flow: This header has no runtime flow, but defines the error and debug contract that XrdTlsSocket returns to callers and that XrdTlsContext uses for construction diagnostics.

State/persistence: No owned state in the header. Implementations use process-global message/debug state.

Dependencies/integration: Forward declares XrdSysLogger and avoids OpenSSL includes in the public header except through implementation. It is included by XrdTlsSocket.hh, XrdTlsContext.cc, XrdTls.cc, and tracing code.

Risks: RC values are ABI-visible because callers may compare enum values. Debug flags are bitmasks used by macros; changes must remain coordinated with XrdTlsTrace.hh.

Test signals: Compile consumers against the public header, validate no OpenSSL header leakage is required, and test that every RC produced by socket/context code has sensible RC2Text output.
