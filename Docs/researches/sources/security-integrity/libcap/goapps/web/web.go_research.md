## sources/security-integrity/libcap/goapps/web/web.go

Purpose: example HTTP server that raises `CAP_NET_BIND_SERVICE` only for binding a privileged port, then drops all privilege before serving requests.

Important APIs/types/functions: flags `--port` and `--skip`; `ensureNotEUID()`, `listen()`, `Handler.ServeHTTP()`, and `main()`. Uses `cap.GetProc`, `Set.Dup`, `GetFlag`, `SetFlag`, `SetProc`, `cap.ModeNoPriv.Set`, `runtime.LockOSThread`, and `net/http`.

Control flow: rejects setuid/root execution, validates port, duplicates current caps, raises effective `NET_BIND_SERVICE` only around `net.Listen` unless skipped, restores original caps via defer, drops to `ModeNoPriv`, and serves responses showing pid/tid/cap state.

State/persistence: opens a listening socket and mutates process capability mode; no file persistence.

Dependencies/integration: Go cap package, Linux file capabilities on the built binary, network stack, HTTP server. `go/Makefile` can optionally set file capabilities on `web`.

Risks: `defer orig.SetProc()` restores caps after `net.Listen` returns, but errors before defer execution are handled by return; `ModeNoPriv` after listen is irreversible; running with `--skip` on low ports demonstrates failure rather than secure behavior.

Test signals: build with file cap `cap_setpcap,cap_net_bind_service=p`, run as non-root on port 80, confirm bind succeeds and request reports empty/no-priv caps.
