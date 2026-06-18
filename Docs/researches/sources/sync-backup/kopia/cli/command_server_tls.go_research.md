<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_tls.go -->
# sources/sync-backup/kopia/cli/command_server_tls.go

## Purpose
Holds TLS and listener support for `server start`: certificate generation, socket activation, TCP or Unix listener creation, serving with persisted or in-memory TLS, and insecure HTTP fallback.

## Important APIs, Types, And Functions
Important functions are `generateServerCertificate`, `startServerWithOptionalTLS`, `maybeGenerateTLS`, `startServerWithOptionalTLSAndListener`, `showServerUIPrompt`, and `checkErrServerClosed`. It uses `tlsutil`, systemd socket activation, and insecure-bind validation.

## Control Flow
`startServerWithOptionalTLS` obtains an activated socket or creates one from `httpServer.Addr`, validates the resolved listener address, and delegates. The listener path optionally writes generated cert/key files, serves with provided PEMs, serves with in-memory TLS, or rejects plaintext unless `--insecure` is set.

## State And Persistence Behavior
Persistent state is limited to generated cert/key PEM files when both output paths and `--tls-generate-cert` are provided. In-memory certificates are ephemeral. The server address and certificate fingerprint are printed to stderr for client discovery.

## Dependencies And Integration Points
Integrates `command_server_start.go`, `internal/tlsutil`, `insecureserverbind`, `coreos/go-systemd/activation`, Go `net/http`, and TLS configuration.

## Risks And Edge Cases
Risks include accidentally overwriting certificates, printing sensitive connection bootstrap material to shared stderr, trusting activated sockets with unexpected network exposure, and only using TLS 1.3 in the in-memory config while `ServeTLS` file mode uses Go defaults.

## Test Signals
Tests should cover generated-file refusal when paths exist, Unix socket address formatting, activated socket count errors, HTTP rejection without `--insecure`, fingerprint output, and graceful `http.ErrServerClosed` handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_tls.go -->
