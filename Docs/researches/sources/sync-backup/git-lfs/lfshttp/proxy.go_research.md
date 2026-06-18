# sources/sync-backup/git-lfs/lfshttp/proxy.go

Purpose: Selects HTTP/S proxy settings from environment and Git config with Git LFS-specific localhost and SOCKS handling.

Important APIs/types/functions: `proxyFromClient` and `getProxyServers`.

Control flow: Per request, reads HTTPS/HTTP proxy and no-proxy values, lets URL-specific or global Git `http.proxy` override environment, normalizes `socks5h://` to `socks5://`, and delegates matching to `httpproxy.Config.ProxyFunc`. Localhost is rewritten to `127.0.0.1` to permit proxying.

State and persistence behavior: Stateless aside from reading client URL config and OS env.

Dependencies and integration points: Used by `Client.Transport`. Depends on `config.URLConfig`, `config.Environment`, and `golang.org/x/net/http/httpproxy`.

Risks and edge cases: `getProxyServers` returns nothing when OS env is nil, even if URL config is present. HTTP requests do not use `HTTPS_PROXY`; they require `HTTP_PROXY` or Git proxy. No-proxy wildcard behavior delegates to `httpproxy`.

Test signals: `proxy_test.go` covers env and Git config precedence, URL-specific config, no-proxy, wildcard, SOCKS, and nil proxy behavior.
