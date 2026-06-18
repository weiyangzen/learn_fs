# sources/user-network-fs/rclone/lib/http/server.go

Source read signal: reviewed complete local file (630 lines, sha256 eda428593afbf497).

Purpose: Provides rclone's reusable HTTP server wrapper with configuration, routing, TLS, socket activation, h2c, base URL stripping, auth, templates, and graceful shutdown.

Important APIs/types/functions: Public pieces include `Help`, `Middleware`, `ConfigInfo`, `Config`, flag methods, `DefaultCfg`, `Server`, options `WithAuth`/`WithConfig`/`WithTemplate`, `NewServer`, `Serve`, `Wait`, `Router`, `Shutdown`, `HTMLTemplate`, `URLs`, `Addr`, and `UsingAuth`. TLS errors include `ErrInvalidMinTLSVersion`, `ErrTLSBodyMismatch`, `ErrTLSFileMismatch`, and `ErrTLSParseCA`.

Control flow: `NewServer` builds a chi router, normalizes base URL, initializes template/TLS, parses response headers, installs CORS/response/auth middleware, then either uses systemd socket-activation listeners or creates Unix/TCP/TLS listeners from config. `newInstance` constructs `http.Server` with timeouts, base context, optional TLS wrapping, and h2c for cleartext. `Serve` starts one goroutine per instance and registers an atexit shutdown; `Shutdown` unregisters and gracefully closes each server.

State and persistence behavior: Holds listener/server instances, TLS config, parsed template, auth config, waitgroup, and atexit handle in memory. Unix sockets are created by listeners and removed by the runtime on close where supported.

Dependencies and integration points: Uses chi, rclone `fs` config flags, `atexit`, `sdactivation`, TLS/x509, and middleware/template/auth helpers. Serve commands mount handlers on `Router`.

Risks and test signals: Auth precedence is subtle when header/cert auth combines with custom/basic/htpasswd. TLS config must reject half-configured cert/key inputs. Socket activation overrides configured addresses. Tests cover Unix, HTTP, base URL, TLS, mutual TLS, h2c, and help prefix.
