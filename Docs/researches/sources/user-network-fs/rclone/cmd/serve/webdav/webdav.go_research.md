<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/webdav/webdav.go -->
# sources/user-network-fs/rclone/cmd/serve/webdav/webdav.go

Source read: complete file, 727 lines, 21369 bytes, sha256 `98bf2afbddbab4f0daee8e059136bcdadbd029b8856b68e49ccd6e16e38c276c`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/webdav/webdav.go_research.md`.

## Purpose
Implements `rclone serve webdav`, adapting rclone VFS to Go's WebDAV filesystem interface with optional directory browsing, zip downloads, ETags, gzip compression, and auth-proxy support.

## Important APIs, types, and functions
`Options`, `Command`, `WebDAV`, `newWebDAV`, `getVFS`, `auth`, `ServeHTTP`, `serveDir`, WebDAV filesystem methods (`Mkdir`, `OpenFile`, `RemoveAll`, `Rename`, `Stat`), `Handle`, `FileInfo`, `DeadProps`, `Patch`, `ETag`, and `ContentType` are the important APIs.

## Control flow
Startup resolves ETag hash options, creates either a fixed VFS or proxy-backed custom auth, constructs `lib/http.Server`, wraps routes with compression/range and server headers, registers WebDAV-only methods, and routes all paths to `ServeHTTP`. Directory GET/HEAD can render HTML or zip; other methods are delegated to `webdav.Handler`, followed by X-OC-Mtime postprocessing on successful COPY/MOVE/PUT.

## State and persistence behavior
Remote state is files/directories/modtimes managed through VFS. Runtime state includes HTTP server, WebDAV memory lock system, optional proxy VFS cache, ETag hash type, and template config. Dead properties expose checksums and lastmodified; PROPPATCH can update modtime.

## Dependencies and integration points
Depends on chi, Go `x/net/webdav`, rclone HTTP server/template/auth, VFS, proxy, hash APIs, and HTTP serve directory helpers.

## Risks and edge cases
Compression must skip Range requests to preserve partial content. Auth-proxy relies on lib/http custom auth storing a VFS in context. ETag and checksum generation may be expensive or unavailable. WebDAV rename overwrite semantics depend on VFS/backend behavior. Directory zip can stream large trees.

## Test signals
`webdav_test.go` covers generic WebDAV backend integration, directory/file HTTP behavior with golden output, gzip for text/PROPFIND, Range no-compression, and rc startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/webdav/webdav.go -->
