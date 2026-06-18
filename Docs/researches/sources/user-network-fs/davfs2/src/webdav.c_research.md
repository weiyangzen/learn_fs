# sources/user-network-fs/davfs2/src/webdav.c

## Purpose
`webdav.c` is davfs2’s Neon-backed WebDAV transport layer. It owns the global HTTP/WebDAV session, TLS/auth/proxy/cookie/header configuration, server capability initialization, path encoding conversion, request execution, lock management, property parsing, file transfer, quota queries, and translation from Neon/HTTP results to filesystem errno values.

## Important APIs, Types, and Functions
- `dav_init_webdav(const dav_args *)`: initializes iconv converters, Neon sockets/session, timeouts, user-agent, redirects, auth callbacks, proxy, TLS trust/client certs, lock store, custom headers, cookies, compression, and property selection.
- `dav_init_connection(path)`: sends OPTIONS, validates WebDAV class 1 unless overridden, registers or disables lock support based on DAV class 2.
- `dav_close_webdav()`: unlocks all stored locks, destroys the session, and shuts down Neon sockets.
- Encoding helpers: `dav_conv_from_utf_8`, `dav_conv_to_utf_8`, `dav_conv_from_server_enc`, `dav_conv_to_server_enc`.
- File/resource operations: `dav_get_collection`, `dav_get_file`, `dav_head`, `dav_put`, `dav_delete`, `dav_delete_dir`, `dav_make_collection`, `dav_move`, `dav_quota`, `dav_set_execute`.
- Lock operations: `dav_lock`, `dav_lock_refresh`, `dav_unlock`, plus private `lock_by_path`, `lock_discover`, `lock_refresh`, and `lock_result`.
- Private callbacks: `auth`, `ssl_verify`, `add_header`, `get_cookies`, `file_reader`, `prop_result`, `quota_result`.
- Error normalization: `get_error()` maps Neon statuses to errno; `get_ne_error()` maps HTTP status codes to errno.

## Control Flow
Initialization builds one global `ne_session` from `dav_args`, then most public operations lazily call `dav_init_connection()` on first use. Paths are escaped using `ne_path_escape()` before requests. `dav_get_collection()` issues a depth-one PROPFIND and `prop_result()` builds a linked list of `dav_props`, normalizing directory slashes, names, etags, modification times, content length, and Apache executable properties. `dav_get_file()` builds a GET with conditional headers, optional decompression, streaming body writes to a cache file, and special redirect handling through a temporary read session. `dav_put()` optionally prechecks with HEAD, applies `If-None-Match`/`If-Match`, uses stored WebDAV locks, uploads by fd, retries after lock discovery on access failure, and refreshes etag/mtime from response or follow-up HEAD.

Locking is conditional on server support and configuration. `dav_lock()` either refreshes existing locks, creates exclusive write locks with configured owner/timeout, or discovers same-owner locks on `EACCES`. `dav_unlock()` removes local lockstore entries on success or benign missing/invalid responses. Shutdown attempts to unlock all tracked resources.

## State and Persistence
Global mutable state includes `session`, request timeouts, `locks`, `owner`, `lock_timeout`, server/proxy credentials, trusted server cert, request behavior flags, property name table, initialization flag, terminal availability, iconv descriptors, Neon debug stream, custom headers, cookie capacity/list, and TLS trust state. Remote persistent effects include WebDAV resource creation/deletion/move/upload, locks, executable properties, and cookie-driven server state. Local persistent effects are downloaded cache file writes through `file_reader()`.

## Dependencies and Integration Points
The module depends heavily on Neon (`ne_session`, auth, SSL, locks, props, redirects, compression, URI/path helpers), libc/POSIX file descriptors and syslog, optional iconv/nl_langinfo, `defaults.h`, `mount_davfs.h` for `dav_args`, and `webdav.h` for exported types. It is consumed by the cache and kernel-facing layers to implement filesystem operations on remote resources.

## Risks and Edge Cases
This file is global-session and not thread-isolated; callers must serialize appropriately or avoid concurrent mounts in one process. Credentials are duplicated into globals and are not visibly scrubbed in `dav_close_webdav()`. `dav_delete_props()` frees a single node only; callers must loop over lists. `dav_get_file()` handles redirects manually for GET only and notes that redirected sessions do not reuse configured client/server cert policy. `create_rd_session()` sets the user-agent on `session` instead of `rd_sess`, likely a bug. `file_reader()` opens with `O_WRONLY | O_TRUNC` but not `O_CREAT`; downloads require an existing cache file. Several fd checks use `<= 0`, treating fd 0 as failure. `dav_put()` can return without closing `fd` if `fstat()` fails. `prop_result()` uses prefix checks that are case-insensitive for paths and then performs duplicate/normalization-sensitive behavior; servers with unusual encoded paths or duplicate names need coverage. Cookie storage ignores attributes and security scope, sending all stored cookies on subsequent requests for the session.

## Test Signals
Unit tests with mocked Neon should cover HTTP-to-errno mapping, OPTIONS capability behavior, no-lock fallback, conditional GET/PUT headers, redirect GET sessions, etag normalization including weak etags, property parsing for directories/files/minimal prop sets, duplicate/slashy names, quota missing-property fallback, lock creation/refresh/discovery/unlock, cookie replacement/capacity, custom header injection, and TLS verification paths with and without terminal. Integration tests need live or simulated WebDAV servers for class 1/2, redirects, broken If-Match behavior, weak etags, gzip, SharePoint href behavior, and quota.
