# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsSocket.hh

Purpose: Declares the public TLS socket wrapper used for TLS handshakes and encrypted I/O over existing file descriptors.

Important APIs/types/functions: Defines RW_Mode combinations for blocking/nonblocking read/write BIOs, HS_Mode for blocking vs nonblocking handshakes, SDType for shutdown style, constructors, Init(), Accept(), Connect(), Context(), getCerts(), Peek(), Pending(), Read(), SetTraceID(), Shutdown(), Write(), NeedHandShake(), and Version().

Control flow: Users can either construct with full parameters and catch exceptions or default-construct and call Init() for error-string return. After Init(), client code calls Connect() and server code calls Accept(); I/O methods may perform implicit handshake if needed.

State/persistence: Implementation state is opaque in XrdTlsSocketImpl. The wrapper never closes the underlying fd.

Dependencies/integration: Includes XrdTls.hh and forward declares context, peer cert wrapper, and XrdNetAddrInfo. It is the boundary between XRootD network code and OpenSSL.

Risks: trace id lifetime is caller-owned. serial=false can expose OpenSSL session concurrency issues. Blocking semantics are subtle because handshake and read/write blocking modes are independent.

Test signals: Compile API users, validate constructor exception and Init() error-string paths, and verify I/O return-code contract under blocking and nonblocking modes.
