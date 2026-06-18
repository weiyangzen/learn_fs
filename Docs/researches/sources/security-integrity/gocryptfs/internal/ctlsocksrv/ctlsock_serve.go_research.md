<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_serve.go -->
# sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_serve.go

- Purpose: Implements the JSON request/response protocol for the control socket and dispatches path encryption/decryption to the mounted frontend.
- Important APIs/types/functions: `type Interface interface`, `type ctlSockHandler struct`, `const ReadBufSize = 5000`, `func Serve(sock net.Listener, fs Interface)`, `func (ch *ctlSockHandler) acceptLoop()`, `func (ch *ctlSockHandler) handleConnection(conn *net.UnixConn)`, `func (ch *ctlSockHandler) handleRequest(in *ctlsock.RequestStruct, conn *net.UnixConn)`, `func sendResponse(conn *net.UnixConn, err error, result string, warnText string)`.
- Control flow and state: uses explicit locking/atomic state for concurrency-sensitive paths; transforms data through encryption/decryption boundaries; treats invalid internal invariants as fatal/panic conditions. Source size is 4660 bytes across 164 lines, read as part of this work item.
- Dependencies and integration points: standard library: encoding/json, errors, fmt, io, net, os, syscall; external/internal modules: github.com/rfjakob/gocryptfs/v2/ctlsock, github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_serve.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: Contains inline test/benchmark hooks or comments; package-level tests should be run for validation.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_serve.go -->
