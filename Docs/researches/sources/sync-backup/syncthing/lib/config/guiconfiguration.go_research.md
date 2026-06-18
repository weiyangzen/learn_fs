# sources/sync-backup/syncthing/lib/config/guiconfiguration.go

## sources/sync-backup/syncthing/lib/config/guiconfiguration.go

Purpose: Defines GUI/API server configuration and helpers for address overrides, auth, TLS, API keys, password hashing, and session-cookie path normalization.

Important APIs/types/functions: `GUIConfiguration` fields include enablement, address, Unix socket permissions, user/password/auth mode, metrics auth bypass, TLS, API key, host/frame security flags, theme, basic-auth prompt, and cookie settings. Methods include `IsAuthEnabled`, `IsOverridden`, `Address`, `UnixSocketPermissions`, `Network`, `UseTLS`, `URL`, `SetPassword`, `CompareHashedPassword`, `IsValidAPIKey`, `prepare`, and `Copy`.

Control flow and state: Environment variable `STGUIADDRESS` overrides stored address, network, and TLS interpretation; Unix schemes return path/network `unix`. `URL` rewrites wildcard TCP hosts to loopback for browser-safe URLs. `prepare` generates a random API key if missing and normalizes non-empty session cookie paths to start with `/`. Passwords are bcrypt-hashed unless they already match a bcrypt-hash regex.

Dependencies and integration: Uses `bcrypt`, `net/url`, environment variables, and `lib/rand`. Consumed by API server startup, authentication middleware, and config defaults.

Risks and test signals: Env overrides can change runtime behavior without persisted config changes. Security-sensitive areas are password hashing, API-key override acceptance, insecure flags, and metrics-without-auth. Tests cover URL rewriting, cookie path normalization, bcrypt hashing/comparison, and default GUI behavior.
