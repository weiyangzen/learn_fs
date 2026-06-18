
# sources/user-network-fs/rclone/backend/http/http.go

## Purpose
This file implements rclone's read-only HTTP backend. It treats HTML directory listings as folders, exposes linked files as objects, supports optional request headers and no-HEAD/no-slash modes, reads selected HTTP metadata, and offers a backend command to update config at runtime.

## Important APIs, Types, And Control Flow
`init` registers the backend, options, command help, and metadata keys. `NewFs` parses options and calls `httpConnection`, which normalizes the endpoint/root and uses `getFsEndpoint` to decide whether the root points to a file or directory. `parseName` and `parse` convert same-host/same-scheme single-level anchor hrefs into listing names. `List` reads an HTML directory and concurrently HEADs potential files to classify files versus directories unless entries already end with `/`. `Object.head` populates size, modtime, content type, content disposition, and other headers. `Open` issues GET and applies option headers. Mutating methods return `errorReadOnly`. `Command("set")` reparses new options and rebuilds the connection. `Metadata` returns supported headers in lower-case keys.

## State And Persistence
The backend stores endpoint URL, parsed root, custom headers, a shared HTTP client, and object metadata from HEAD/GET responses. It does not persist remote data and all write/delete/mkdir/update operations fail read-only. Runtime `set` updates in-memory config only for the running backend instance.

## Dependencies And Integration Points
It depends on Go `net/http`, `net/url`, MIME parsing, `golang.org/x/net/html`, rclone `fs`, `fshttp`, `rest`, hash interfaces, metadata interfaces, and command plumbing. It implements `fs.Fs`, `fs.PutStreamer` only to return read-only errors, `fs.Object`, `fs.MimeTyper`, `fs.Commander`, and `fs.Metadataer`.

## Risks And Test Signals
`List` uses `sync.WaitGroup.Go`, so it depends on the Go version/runtime API available in this source tree. No-HEAD mode returns unknown size/time and can misclassify HTML files when `NoSlash` is set. `parseName` excludes query strings and cross-host/scheme links, which is safe but may skip valid download URLs. `Remote` can be overridden by `Content-Disposition` filename, which may surprise path identity. Tests should cover all listing parsers, root-as-file detection, no-head behavior, custom headers, metadata extraction, range GET options, read-only errors, no-escape URLs, and backend `set`.
