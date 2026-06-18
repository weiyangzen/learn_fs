<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_listen.go -->
# sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_listen.go

- Purpose: Creates a Unix control-socket listener and safely removes only stale orphan socket files before binding.
- Important APIs/types/functions: `func cleanupOrphanedSocket(path string)`, `func Listen(path string) (net.Listener, error)`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 977 bytes across 45 lines, read as part of this work item.
- Dependencies and integration points: standard library: errors, io/fs, net, os, syscall, time; external/internal modules: github.com/rfjakob/gocryptfs/v2/internal/tlog. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_listen.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: No direct tests in this file; rely on package integration tests and callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/ctlsock_listen.go -->
