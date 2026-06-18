<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize.go -->
# sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize.go

- Purpose: Canonicalizes user-supplied control-socket paths for FUSE-relative use and rejects traversal above the mount root.
- Important APIs/types/functions: `func SanitizePath(path string) string`.
- Control flow and state: is mostly stateless helper or interface assertion code. Source size is 651 bytes across 34 lines, read as part of this work item.
- Dependencies and integration points: standard library: path/filepath, strings. It integrates with the surrounding gocryptfs package through the source path `sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize.go` and the declarations listed above.
- Risks and review notes: main risk is compatibility drift because nearby packages depend on these small constants/helpers.
- Test signals: Nearby test signal: `sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize_test.go` covers related behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/internal/ctlsocksrv/sanitize.go -->
