
# sources/user-network-fs/rclone/backend/koofr/koofr.go

## Purpose
Implements the rclone backend for Koofr-compatible storage providers, including Koofr, Digi Storage, and custom endpoints.

## Important APIs, Types, And Control Flow
Key types are `Options`, `Fs`, and `Object`. Registration declares provider-specific config options, encoding, credentials, mount selection, and mtime capability. `NewFs` parses config, applies provider defaults, reveals the password, creates a Koofr client with basic auth, selects the configured or primary mount, and detects file roots. Object methods expose remote name, size, MD5, millisecond mtime, range reads, overwriting uploads, and delete. Fs methods cover listing, object lookup, upload/stream upload, recursive mkdir, rmdir-empty check, server-side copy/move/dirmove, quota, purge, and public links.

## State And Persistence
Persistent state is backend config: provider, endpoint, mount ID, user, obscured password, `setmtime`, and encoding. Runtime state is small: client, selected mount ID, root, feature table, and object `FileInfo`. Remote persistence is delegated to Koofr file, folder, mount, and link APIs.

## Dependencies And Integration Points
Uses rclone `fs`, config, encoder, fshttp, hash APIs, plus `github.com/koofr/go-koofrclient` and `go-httpclient`. Implements rclone optional interfaces such as put streaming, copy, move, dir move, purge, about, and public link.

## Risks And Test Signals
Important risks are unchecked type assertions in copy/move/dirmove, provider endpoint inference for legacy configs, mount selection errors, translating Koofr 400/404 into rclone errors, duplicate mkdir races, and public-link URL rewriting assumptions. Test signals should include provider defaulting, root-file detection, mkdir idempotency, error translation, range reads, copy/move across mounts, quota unit conversion, and link URL generation.
