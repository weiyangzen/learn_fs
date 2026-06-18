# sources/user-network-fs/rclone/fs/fshttp/http.go

## Purpose
`http.go` is rclone's shared HTTP transport and client factory. It translates global configuration into `http.Transport` settings, wraps requests for user-agent/header injection, logging, curl/debug dumps, low-level trace logging, Prometheus metrics, server-clock checks, cookie jar support, client certificate loading and hot reload, custom CA roots, proxies, HTTP/2 disabling, TCP or Unix-socket dialing, and request throttling.

## Important APIs, types, and functions
Key APIs are `LoadKeyPair`, `NewTransportCustom`, `NewTransport`, `NewClient`, `NewClientCustom`, `NewClientWithUnixSocket`, `Transport`, `SetRequestFilter`, and `RoundTrip`. `UnixSocketConfig` is an advanced config option. Helper logic includes auth scrubbing (`cleanAuths`, `cleanCurl`), server time validation, certificate expiry detection/reload, retryable-response classification for dump-on-error, and `newClientTrace` for `httptrace.ClientTrace`.

## Control flow
`NewTransportCustom` copies Go's default transport, applies rclone timeouts, proxy, TLS, CA, compression, idle-connection, HTTP/2, and custom dialer settings, then wraps it in `Transport`. Each `RoundTrip` reloads an expiring client cert if needed, applies TPS limits and configured headers, optionally filters the request, produces request/body/curl/trace dumps depending on dump flags, executes the underlying transport, dumps retryable errors/responses, records metrics, and checks the server `Date` header once per host.

## State and persistence behavior
State is process-local: a singleton transport guarded by `sync.Once`, a package cookie jar, checked-host cache, log mutex, and certificate reload mutex. Persistent state is only external file input for cert/key/CA files; no HTTP state is written except cookies in memory and logs/metrics emitted through other subsystems.

## Dependencies and integration points
This package depends on rclone `fs.ConfigInfo`, `accounting.LimitTPS`, `fs.DumpFlags`, `fs.HTTPOption`, `obscure.Reveal`, `structs.SetDefaults`, `NewDialer`, Prometheus metrics from `prometheus.go`, publicsuffix cookie jars, `http2curl`, and PKCS#8 parsing. Backends and OAuth clients call these factories to share consistent transport behavior.

## Risks and edge cases
The global `NewTransport` only reflects the first configuration until `ResetTransport` is used in tests. `LoadKeyPair` must handle encrypted PKCS#8, legacy encrypted PEM, RSA, EC, cert chains, and obscured passwords. Dumping bodies can consume or expose data if flags are wrong, so auth scrubbing is critical. Fatal errors during TLS setup terminate the process. Server-clock checks depend on trustworthy `Date` headers.

## Test signals
`http_test.go` covers auth scrubbing, curl redaction, and live client-certificate reload behavior. Wider coverage is indirect through every backend using `fshttp.NewClient*`, especially dump flags, custom headers, proxies, TLS, metrics, and Unix-socket transports.

Source-read signal: reviewed complete local file (703 lines). Types observed: `Transport`. Functions/methods observed: `ResetTransport`, `LoadKeyPair`, `NewTransportCustom`, `NewTransport`, `NewClient`, `NewClientCustom`, `NewClientWithUnixSocket`, `newTransport`, `SetRequestFilter`, `checkServerTime`, `cleanAuth`, `cleanAuths`, `cleanCurl`, `isCertificateExpired`, `reloadCertificates`, `isRetryableResponse`.
