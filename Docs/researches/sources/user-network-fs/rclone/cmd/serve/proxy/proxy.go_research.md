<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxy.go -->
# sources/user-network-fs/rclone/cmd/serve/proxy/proxy.go

Source read: complete file, 346 lines, 10483 bytes, sha256 `371767e31854fa8feab1d26361e498507bd23e2d6c5cb2a64639890be38a4a09`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/proxy/proxy.go_research.md`.

## Purpose
Implements the programmable authentication proxy used by rclone serve protocols to derive per-user backend configuration from an external command. It lets servers authenticate an incoming password or public key, run a JSON stdin/stdout helper, create a backend from the returned config, and cache a VFS for subsequent requests.

## Important APIs, types, and functions
`OptionsInfo`, `Options`, and global `Opt` register the `auth_proxy` global option. `Proxy` stores the split command line, request context, VFS options, and a `lib/cache.Cache`. `cacheEntry` stores the VFS plus a SHA-256 credential guard. `New`, `run`, `generateCacheKey`, `call`, `Call`, and `Get` are the core API.

## Control flow
`Call` derives a credential-aware HMAC cache key and first checks the VFS cache. On miss, `call` runs the proxy command with either `user/pass` or `user/public_key`, validates returned `type` and `_root`, fills backend defaults, constructs an rclone Fs via `fsInfo.NewFs`, wraps it in VFS, and stores it. `run` obscures any fields named by `_obscure` before backend construction.

## State and persistence behavior
Persistent state is remote backend state created by the returned config; local state is an in-memory VFS cache keyed by username and a process-random HMAC of the auth secret. The raw password is not persisted; only a SHA-256 hash is kept in `cacheEntry` for collision defense. The HMAC key is process local, so cache names are not stable across restarts.

## Dependencies and integration points
Depends on `os/exec`, JSON encoding, `fs`, `fs/cache`, `configmap`, `obscure`, `lib/cache`, and VFS packages. It is integrated by SFTP, WebDAV, S3, and test helpers through `proxy.New`, `Proxy.Call`, and `Proxy.Get`.

## Risks and edge cases
Command parsing uses `strings.Fields`, so quoted paths or arguments are not shell interpreted. Proxy helpers must return complete safe config because environment/CLI config is not merged. The cache key appears in backend names and logs, so the HMAC construction is important. Global `proxy.Opt` checks in some callers can diverge from passed `proxyOpt` if modified carelessly.

## Test signals
`proxy_test.go` exercises command success, helper failure, obscuring, password and public-key calls, cache reuse, and cache miss retrieval. Serve protocol integration tests also run auth-proxy modes through `servetest`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxy.go -->
