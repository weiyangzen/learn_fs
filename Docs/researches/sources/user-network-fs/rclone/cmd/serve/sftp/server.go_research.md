<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/server.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/server.go

Source read: complete file, 456 lines, 13791 bytes, sha256 `86d437581d1327e1e1107d5379a1a3ff1017cd19d21d68c80726fb1fb9c698c1`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/server.go_research.md`.

## Purpose
Builds and runs the SSH server for `rclone serve sftp`, including authentication, host key loading/generation, listener setup, and proxy integration.

## Important APIs, types, and functions
`server` stores Fs, options, fixed VFS or proxy, SSH config, listener, and stopped channel. `newServer`, `configure`, `acceptConnections`, `acceptConnection`, `getVFS`, `Serve`, `Shutdown`, key loading, authorized key loading, and RSA/ECDSA/Ed25519 key generation are central.

## Control flow
`configure` rejects conflicting auth-proxy and authorized-keys flags, loads authorized keys, enforces that some auth is configured unless `--no-auth`, builds password and public-key callbacks, loads or generates host keys under the cache dir, then obtains a socket-activation listener or binds TCP. Accepted SSH connections authenticate, map proxy credentials to a cached VFS key when needed, and hand channels to `connection.go`.

## State and persistence behavior
Persistent local state can include generated host key files in the rclone cache directory. Runtime state includes listener, SSH config, fixed VFS or proxy VFS cache, and per-connection permissions extensions.

## Dependencies and integration points
Depends on crypto key generation, `x/crypto/ssh`, rclone config/cache/env/file helpers, sdactivation, proxy, VFS, and server connection handlers.

## Risks and edge cases
Authentication safety depends on flag validation and constant-time user/pass checks. Auto-generated host keys persist and file permissions matter. `proxy.Opt.AuthProxy` is checked globally in places instead of only the passed proxy options, which can surprise tests or embedding. `loadAuthorizedKeys` silently skips parse errors while bytes remain only when no key parsed.

## Test signals
SFTP integration, handler, rc, and auth-proxy tests exercise listener startup, auth, VFS mapping, and shutdown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/server.go -->
