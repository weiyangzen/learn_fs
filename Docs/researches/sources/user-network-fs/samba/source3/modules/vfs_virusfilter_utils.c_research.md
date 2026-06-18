# sources/user-network-fs/samba/source3/modules/vfs_virusfilter_utils.c

## Purpose
This file supplies shared utilities for virusfilter backends and the core: Samba substitution expansion, stackable file moves, line-oriented Unix socket I/O with timeouts, in-memory scan result caching, and shell command environment construction/execution.

## Important APIs, Types, and Functions
`virusfilter_string_sub()` wraps Samba substitution for service/user/path variables. `virusfilter_vfs_next_move()` renames through the next VFS module and deliberately refuses cross-device `EXDEV`. I/O helpers include `virusfilter_io_new()`, EOL/timeout setters, `virusfilter_io_connect_path()`, `virusfilter_io_disconnect()`, `write_data_iov_timeout()`, `virusfilter_io_write*()`, `virusfilter_io_readl()`, and `virusfilter_io_writefl_readl()`. Cache helpers create a `memcache`, add/get/rename/remove/purge entries keyed by directory plus filename, and duplicate/free cache entries safely. Shell helpers include `virusfilter_env_set()`, `virusfilter_shell_set_conn_env()`, and `virusfilter_shell_run()`.

## Control Flow
Socket connect builds an AF_UNIX address, opens a nonblocking close-on-exec socket, and wraps it as a tstream. Write/read operations create short-lived tevent contexts and poll send/receive requests with deadlines. `virusfilter_io_readl()` first drains any existing complete line from the buffer, otherwise reads more data until the configured EOL appears. Cache insertion steals the scan report into a talloc cache entry, while lookups copy entries out so callers can free them independently.

## State and Persistence
Runtime state lives in `struct virusfilter_io_handle` and `struct virusfilter_cache`. The cache is per-process memory only and has time-based expiry. Shell execution may produce external side effects through administrator-configured commands.

## Dependencies and Integration Points
The file depends on Samba tsocket/tstream/tevent, memcache, strv, loadparm substitution, and `smbrun`. It is built as `VFS_VIRUSFILTER_UTILS` only when `vfs_virusfilter` is enabled.

## Risks
`virusfilter_io_readl()` appears to calculate `read_size` with `MIN(pending, 1)` followed by `MAX(..., remaining)`, which can request the full remaining buffer rather than the smaller pending amount; this deserves focused review under nonblocking tstream behavior. Formatted writes do not guard against `vsnprintf()` output equal to or larger than the fixed buffer before appending EOL. Cache expiry removal passes an already combined `directory/fname` as `fname` back into `virusfilter_cache_remove()`, which may build a mismatched key. Shell command execution is sanitized but still administrator-controlled and security-sensitive.

## Test Signals
Unit tests should cover partial-line buffering, multiple lines in one read, timeout/error paths, overlong scanner lines, cache add/get/expiry/rename/remove key behavior, cross-device rename refusal, environment variable population, and sanitized versus unsanitized shell execution.
