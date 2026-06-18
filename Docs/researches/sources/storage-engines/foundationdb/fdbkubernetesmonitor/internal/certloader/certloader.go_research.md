# sources/storage-engines/foundationdb/fdbkubernetesmonitor/internal/certloader/certloader.go

Purpose: implements hot-loading TLS certificate support for the monitor HTTP server. It lets the Prometheus/pprof endpoint use `tls.Config.GetCertificate` so certificate material can be reloaded without restarting the monitor process.

Important APIs and types: `CertLoader` stores cert/key paths, a cached `tls.Certificate`, the cached key-file modification time, a mutex, and a logger. `NewCertLoader(logger, certFile, keyFile)` constructs it. `GetCertificate(*tls.ClientHelloInfo)` checks the key file mtime, returns the cached pair when unchanged, or reloads with `tls.LoadX509KeyPair`.

Control flow: each TLS handshake calls `GetCertificate`. The method stats the key file first, locks around cache inspection/update, compares `stat.ModTime()` with `cachedCertModTime`, logs reloads, and replaces the cached pair on successful load.

State and persistence behavior: no persistent writes. Runtime state is only the cached certificate and key-file mtime. The mtime source is the key file, not the cert file.

Dependencies and integration points: used by `monitor.go` when `certificate-path` or `certificate-key-path` is configured. Depends on `crypto/tls`, `os.Stat`, and `go-logr`.

Risks: certificate-only changes may not reload if the key file mtime is unchanged. Supplying only one of cert/key paths causes the HTTPS branch to run and fail during load. Concurrent handshakes are serialized through one mutex during reload.

Test signals: no direct tests in this subset; behavior is indirectly reachable through monitor HTTPS startup, but reload edge cases are not covered.
