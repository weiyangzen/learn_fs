# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsSocket.cc

Purpose: Implements XrdTlsSocket, a TLS I/O wrapper around an existing file descriptor and an XrdTlsContext-generated SSL session.

Important APIs/types/functions: XrdTlsSocketImpl stores SSL pointer, context, fd, trace id, handshake timeout/state, fatal error marker, client/server role, connection flags, and serialization policy. Accept(), Connect(), Init(), Peek(), Pending(), Read(), Write(), Shutdown(), NeedHandShake(), Version(), getCerts(), Diagnose(), Err2Text(), NeedHS(), and Wait4OK() are implemented here.

Control flow: Init() obtains SSL from context, sets connect/accept state, creates socket BIOs according to read/write blocking mode, handles nonblocking handshake setup for blocking-read server sockets, and attaches BIOs. Accept() loops SSL_accept(), verifies peer cert if configured, handles WANT_READ/WANT_WRITE by either returning nonblocking RC or polling, and restores blocking mode when needed. Connect() loops SSL_connect(), then validates hostname through XrdTlsNotary if requested. Read/Write/Peek use SSL_read/write/peek, translate OpenSSL WANT states, and optionally block with poll(). Shutdown() performs forced/fast/clean shutdown then frees SSL.

State/persistence: State is per socket object and no fd ownership is taken. Fatal SSL/SYSCALL errors are remembered to avoid later OpenSSL calls that could crash. The traceID pointer must outlive the socket.

Dependencies/integration: Depends on OpenSSL SSL/BIO/ERR, fcntl/poll/socket APIs, XrdSysE2T, XrdSysMutex, XrdTlsContext, XrdTlsNotary, XrdTlsPeerCerts, and trace macros.

Risks: Blocking mode transitions mutate the underlying fd and affect other users of the same fd. Wait4OK uses handshake timeout only until hsDone; later I/O can block indefinitely when configured blocking. fatal state protects against unsafe reuse but requires callers to respect return codes. Non-serialized mode shifts thread-safety responsibility to callers.

Test signals: Integration tests with client/server TLS sockets should cover every RW_Mode and HS_Mode, WANT_READ/WANT_WRITE nonblocking returns, handshake timeout, hostname validation failure, missing/failed peer cert verification, shutdown variants, fatal error reuse, and fd blocking restoration.
