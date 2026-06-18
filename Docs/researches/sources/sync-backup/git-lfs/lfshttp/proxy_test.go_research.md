# sources/sync-backup/git-lfs/lfshttp/proxy_test.go

Purpose: Tests proxy selection precedence and no-proxy behavior.

Important APIs/types/functions: Exercises `NewClient`, `proxyFromClient`, and generated proxy functions.

Control flow: Each test builds a client with env/config proxy settings, creates a request, invokes the proxy function, and asserts returned proxy URL or nil.

State and persistence behavior: Uses map-backed env/config only; no external state.

Dependencies and integration points: Validates integration with Git URL config and `httpproxy` matching.

Risks and edge cases: Confirms Git config overrides environment, URL-specific proxy overrides global, `NO_PROXY` suppresses proxy, wildcard no-proxy works, and `socks5h` is normalized.

Test signals: Good coverage for proxy decision logic. It does not test lowercase env variables separately beyond implementation paths.
