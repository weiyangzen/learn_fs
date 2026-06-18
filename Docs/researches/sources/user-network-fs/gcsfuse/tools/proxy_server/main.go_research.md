# sources/user-network-fs/gcsfuse/tools/proxy_server/main.go

Purpose: executable proxy server for integration tests, supporting HTTP forwarding with retry injection and gRPC forwarding with metadata validation.

Important APIs/types/functions: flags `config-path`, `debug`, `log-file`; globals `gConfig`, `gOpManager`, `gPort`; `ProxyHandler.ServeHTTP`; `AddRetryID`; `ProxyServer.Start`; `main`; `GRPCProxyServer.Start`.

Control flow: main parses config, opens log file, initializes operation manager, and starts HTTP or gRPC based on `proxyType`. HTTP handler copies request headers/body to target, deduces request type, optionally creates a retry test and header, forwards, rewrites redirect `Location` hosts to the proxy port, copies response headers/body, and logs timing. Servers listen on random ports and block until SIGINT/SIGTERM.

State/persistence behavior: global config/operation manager/port state is shared across handlers. Operation manager retry counts mutate across requests. Logs are appended to the supplied log file.

Dependencies/integration: used by integration tests as a custom endpoint. Depends on request mapper, emulator helper, operation manager, and gRPC proxy.

Risks/test signals: global mutable state complicates parallel tests. `http.Client{}` has no timeout, so stalled target requests can hang. Typos in log text do not affect behavior but reduce polish.
