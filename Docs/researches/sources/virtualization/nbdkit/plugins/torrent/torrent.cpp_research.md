# File Research: sources/virtualization/nbdkit/plugins/torrent/torrent.cpp

Implements the `torrent` nbdkit plugin, serving one file from a torrent or magnet link as a read-only NBD export with on-demand piece download.

Key behavior:
- `.config` accepts one `torrent` source, optional `file`, optional `cache`, and selected libtorrent settings (`connections-limit`, rate limits, interfaces, user-agent).
- Torrent source supports local torrent files, `file:` URLs, and magnet URIs. HTTP/FTP torrent-file download is reserved but not implemented.
- If no cache directory is supplied, `.config_complete` creates a temporary directory under `TMPDIR` or `LARGE_TMPDIR` and marks it for cleanup.
- `.config_complete` configures DHT bootstrap nodes, sequential mode, tracker behavior, end-game behavior, and alert categories.
- `.after_fork` creates the libtorrent session and starts a background alert thread.
- The alert thread waits for libtorrent alerts, logs them, handles metadata/add-torrent alerts, records the torrent handle, and broadcasts a condition when pieces finish.
- `got_metadata` selects the served file. If `file=` was omitted, it picks the largest file in the torrent. It records file index and size.
- `.preconnect` waits until metadata has arrived by waiting for a piece-completion condition if the file index is still unset.
- `.open` opens the selected cached file read-only, waiting for it to appear if no piece has created it yet.
- `.pread` maps file offsets to torrent pieces, raises missing piece priority to top, waits until each needed piece is present, then reads from the cache file.
- `.cache` similarly raises piece priority without waiting for completion.
- `.block_size` advertises torrent piece size as preferred request size when it is between 512 bytes and 1 MiB.
- `.unload` removes the torrent from the session, optionally deletes downloaded files, runs `rm -rf` on the generated cache directory, frees globals, and deletes the libtorrent session.
- Thread model is `NBDKIT_THREAD_MODEL_PARALLEL`; global torrent state is protected by a mutex/condition where needed.

Dependencies:
- libtorrent alert/session/torrent APIs.
- pthreads.
- nbdkit API v2.

Notes and risks:
- The alert thread runs an infinite loop and is not explicitly joined on unload.
- Temporary cache cleanup uses `system("rm -rf %s")` without shell quoting; the code relies on generated temporary paths or trusted user `TMPDIR`.
- The plugin is read-only by omission: no write callbacks are implemented.
- The comparison `ti->files().file_path(i) == file` relies on C++ string comparison with a C string.
