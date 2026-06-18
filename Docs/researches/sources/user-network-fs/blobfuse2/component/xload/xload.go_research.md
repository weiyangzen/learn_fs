## sources/user-network-fs/blobfuse2/component/xload/xload.go

Purpose: Blobfuse2 component that preloads a remote read-only filesystem into a local cache path and serves subsequent opens from that cache.

Important APIs and flow: `Configure` enforces global `read-only`, reads xload config, resolves block size from xload or stream config, resolves cache path from xload or file cache config, rejects path equal to mount path, creates empty path, parses mode, sets permissions, worker count, pool size, and cancellation context. `Start` creates a block pool and stats manager, supports only `PRELOAD`, builds downloader stages, starts stats, chains lister -> splitter -> data manager, and starts components in reverse. `Stop` cancels context, stops stages/stats/pool with timeout, then cleans local cache. `OpenFile` locks a per-file lock, downloads on priority if missing, opens the cached file, marks the handle cached, and stores Unix FD. `ReleaseFile` decrements the lock count.

State and persistence: Local cache files live under `xl.path` during mount and are removed on stop. Runtime state includes block pool, stats, stage list, file locks, and context.

Risks: Upload/sync unsupported. Stop timeout may leave goroutines running. `ReleaseFile` does not close the underlying file handle, relying on upstream/native release semantics. Empty-directory requirement can reject reuse. Tests cover config, start/stop, chain, open-on-demand, and unsupported modes.
