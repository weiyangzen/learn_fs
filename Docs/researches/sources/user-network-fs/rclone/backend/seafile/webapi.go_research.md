# sources/user-network-fs/rclone/backend/seafile/webapi.go

Purpose: low-level Seafile Web API adapter used by `seafile.go` and object code. It translates backend actions into REST calls, encodes/decodes names and paths, maps selected HTTP statuses to rclone errors, and handles upload/download link mechanics.

Important APIs/types/functions: constants `APIv20` and `APIv21` select Seafile API roots; `ErrorInternalDuringUpload` signals retryable single-use upload-link failure. Functions cover account auth, server/account info, library CRUD/decrypt/trash cleanup, directory list/detail/create/rename/move/delete, file detail/delete/download/upload/share-link/copy/move/rename, and `decodeFileInfo`.

Control flow: most functions build `rest.Opts`, call through `f.pacer`, and use `f.shouldRetry`. JSON APIs use `CallJSON`; form-only Seafile endpoints manually build URL-encoded bodies. `getAuthorizationToken` is intentionally callable without an `Fs` for configuration-time 2FA. Upload first gets a single-use upload URL elsewhere, posts multipart data, and treats HTTP 500 as `ErrorInternalDuringUpload` so callers can fetch a new link. Download accepts absolute or relative download links and compensates when encrypted libraries ignore HTTP range requests by discarding bytes client-side and wrapping a limited reader.

State and persistence behavior: this file mostly has no durable state, but it mutates decoded API result fields into rclone standard encoding and relies on the shared pacer. It consumes auth headers already installed on `f.srv`.

Dependencies/integration: depends on rclone `rest`, `fs`, `readers`, Seafile API DTOs, `net/url`, `net/http`, and `encoder` behavior via `f.opt.Enc`. It is tightly integrated with `seafile.go` path/library resolution and `Object` upload/download.

Risks/test signals: high-risk areas are undocumented API v2.1 endpoints, inconsistent status mapping, form-body encoding, single-use upload URLs, and client-side range emulation for encrypted libraries. No direct tests are listed for this file; integration tests are the main signal.
