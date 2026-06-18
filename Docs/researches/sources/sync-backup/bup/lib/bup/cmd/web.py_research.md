# sources/sync-backup/bup/lib/bup/cmd/web.py

## Purpose
`web.py` serves a read-only HTTP view of a bup repository using Tornado. It lists directories with optional metadata/hash/hidden/human-size query parameters and streams file content.

## APIs and Control Flow
Parameter helpers (`ParamInfo`, `request_params`, `encode_query`, `from_req_bool`) validate and normalize query state. `_compute_breadcrumbs`, `_contains_hidden_files`, and `_dir_contents` prepare listing template data from VFS resolution. `BupRequestHandler` overrides path argument decoding, handles GET/HEAD, resolves paths with metadata, redirects directories to trailing slash, renders `list-directory.html`, sets file headers (`Last-Modified`, `Content-Type`, `Etag`, `Content-Length`), and streams file chunks with deferred header setting. `main(argv)` parses inet or `unix://` bind address, opens `LocalRepo`, configures Tornado static/template paths, binds sockets, optionally opens a browser, and starts the IOLoop. SIGTERM stops the loop.

## State, Dependencies, Integration, Risks, Tests
Persistent state is none, but it exposes repository data over HTTP for the process lifetime. Dependencies include Tornado, `vfs`, `metadata`, `xstat`, resource templates/static assets, MIME types, and local repo access. Risks include debug mode enabled, broad exception-to-500 handling, strict query rejection producing unhandled `ValueError`, hidden-file double traversal, byte/path quoting issues, UNIX socket/browser incompatibility, and response headers delayed until first chunk. Test signals include directory redirect/listing, query normalization, hidden/meta/hash rendering, HEAD vs GET headers, file streaming errors, address parsing, SIGTERM shutdown, and missing Tornado failure.
