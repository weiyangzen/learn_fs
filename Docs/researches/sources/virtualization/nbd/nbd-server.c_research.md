# File Research: sources/virtualization/nbd/nbd-server.c

## Purpose
Implements the `nbd-server` daemon: configuration parsing, socket setup, modern NBD negotiation, export selection, TLS negotiation, request dispatch, backend file I/O, copy-on-write support, transaction logging, treefile mode, and process/thread lifecycle management.

## Main Entry Points
- `main()` initializes logging/configuration, parses command-line and config-file exports, daemonizes when requested, opens listening sockets, drops privileges, initializes optional GnuTLS state, and enters `serveloop()`.
- `cmdline()` parses legacy command-line export syntax and server options.
- `parse_cfile()` parses GLib key-file configuration, including `[generic]` global settings and per-export groups.
- `setup_servers()`, `open_modern()`, and `open_unix()` create TCP and Unix-domain listening sockets and install signal handlers.
- `serveloop()` accepts connections, monitors child IPC sockets, handles SIGCHLD/SIGTERM/SIGHUP, and appends newly configured exports on reload.
- `handle_modern_connection()` forks per connection unless `dontfork` is enabled, performs negotiation, and starts request serving.
- `negotiate()` implements fixed new-style negotiation and option dispatch for export name, list, abort, STARTTLS, INFO/GO, and structured replies.
- `mainloop_threaded()` reads NBD requests, logs them when enabled, consumes write payloads, and queues work on a GLib thread pool.
- `handle_request()` dispatches read, write, flush, trim, and write-zeroes requests.

## Internal Mechanics
Configuration maps textual parameters to `SERVER` fields and flags. Export groups specify backing path, size, auth file, virtualization mode, COW, treefiles, waitfile, temporary file creation, trim/flush/FUA exposure, TLS enforcement, splice, datalog, and max connections. Included config directories are scanned for `*.conf` snippets.

Negotiation starts with `INIT_PASSWD`, option magic, and fixed-newstyle flags. TLS may be required globally or per export. `NBD_OPT_LIST` lists configured exports when enabled, hiding TLS-only exports before STARTTLS. `NBD_OPT_EXPORT_NAME` and `NBD_OPT_GO` call `commit_client()` to enforce max-client count, derive the peer name and virtualized export path, check ACLs, run prerun hooks, open/export backend storage, prepare transaction logs, and initialize COW/waitfile state.

The I/O path abstracts backend storage through `get_filepos()`, `rawexpread()`, and `rawexpwrite()`. Multifile exports map offsets across a `GArray` of `FILE_INFO`; treefile exports open per-4KiB files on demand; waitfile mode initially records writes into a diff file until the real file appears. COW mode tracks dirty 4KiB pages in `difmap`, reading unmodified data from the base export and modified pages from a per-client diff file.

Replies are serialized under `client->lock`. Ordinary replies use `struct nbd_reply`; structured replies use `send_structured_chunk*()` and `READ_CTX` to split read data or report structured errors. Optional `splice()` paths avoid userspace copies for non-TLS exports when supported.

## Dependencies
Uses GLib arrays/hash tables/key files/thread pools, POSIX sockets/fork/signals/select/pselect, pthread mutex/rwlock primitives, POSIX semaphores, file I/O, optional Linux `splice`, `fallocate`, `BLKDISCARD`, optional Windows zero-data support, and optional GnuTLS. Relies on local protocol helpers from `cliserv.h`, `nbd.h`, `nbd-helper.h`, `nbdsrv.h`, `backend.h`, and `treefiles.h`.

## Risks and Notes
The file mixes daemon-global state, per-export state, per-client state, and per-request worker state, so concurrency behavior depends on disciplined use of `client->lock`, export rwlocks, semaphores, and parent-child IPC. `bad_range()` checks `req->from + req->len` directly, which is sensitive to unsigned overflow. `handle_info()` uses byte-order conversion functions in a semantically confusing way for inbound fields, even if `htonl` and `ntohl` are equivalent on common platforms. Structured error payload fields are not consistently converted at the call site. Some cleanup paths after negotiation or partial client setup return `false` without releasing every object initialized earlier. The COW `difmap` allocation uses `exportsize / DIFFPAGESIZE`, so exports whose size is not a whole diff page need careful boundary assumptions.
