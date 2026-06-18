# sources/sync-backup/casync/src/casync-http.c

## Purpose
`casync-http.c` is the HTTP/HTTPS/FTP/SFTP helper subprocess used by `CaRemote`. It speaks the casync remote frame protocol on stdin/stdout and uses libcurl to fetch archive, index, and chunk URLs from remote stores.

## Important APIs, Types, and Functions
Global arguments capture protocol, verbosity, log level, rate limit, and quit signals. `robust_curl_easy_perform()` retries transient `CURLE_COULDNT_CONNECT` failures with linear backoff. `process_remote()` drives a `CaRemote` until a requested condition is met, such as writable buffers, pending requests, unwritten output, or finish. `write_index()`, `write_index_eof()`, `write_archive()`, and `write_archive_eof()` bridge curl callbacks to remote file frames. `write_buffer()` accumulates curl data with protocol-size bounds. `chunk_url()` constructs `<store>/<first4>/<chunk>.cacnk`. `acquire_file()` fetches index/archive URLs and aborts the remote on protocol-level failures. `run()` configures `CaRemote`, configures curl, streams archive/index, then loops serving chunk requests from one or more stores.

## Control Flow
`main()` installs signal handlers, parses protocol from argv[0], parses options, and supports only the `pull` verb. `run()` converts dash placeholders to NULL URLs, advertises readable services based on provided URLs/stores, binds the remote to stdio, configures curl protocol limits and optional rate limiting, fetches archive and index first, then waits for chunk request frames. For each chunk request it builds a URL, fetches into a buffer, sends either `CA_PROTOCOL_CHUNK` with compressed data or `CA_PROTOCOL_MISSING`, flushes remote output, and repeats until no stores or remote EOF.

## State and Persistence
The helper itself persists nothing. It buffers downloaded data in memory up to frame limits and relies on `CaRemote` for protocol buffers. Curl may use `.netrc` optionally for credentials. Signal handlers set a global quit flag for graceful termination.

## Dependencies and Integration Points
The file depends on libcurl, `caprotocol.h`, `caremote.h`, `cautil.h`, `realloc-buffer.h`, and utility logging/parsing. `caremote.c` launches helpers named `casync-<scheme>` from `CASYNC_PROTOCOL_PATH` for URL-style remotes, so this binary is selected by executable name containing http, https, ftp, or sftp.

## Risks
Only `pull` is implemented; pushing via HTTP is not supported here. HTTP 404 maps to `ENOMEDIUM`, while other HTTP/FTP/SFTP failures abort or produce missing chunks depending on phase. `chunk_url()` strips query/semicolon suffixes and trailing slashes, so unusual store URLs need coverage. `write_buffer()` protects frame size but accumulates whole chunks/index fragments in memory. The store rotation variable `current_store` is not incremented in the visible loop, so fallback stores may not actually rotate.

## Test Signals
Script tests that use `CASYNC_PROTOCOL_PATH` can exercise helper-based pull paths when the helper binaries are built. Additional tests should cover HTTP status handling, SFTP status handling, multi-store fallback rotation, rate-limit option parsing, and graceful signal exit.
