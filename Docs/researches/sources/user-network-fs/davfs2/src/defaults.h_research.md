<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/davfs2/src/defaults.h -->
# Research: sources/user-network-fs/davfs2/src/defaults.h

Purpose: central defaults and constants for davfs2 runtime, cache, HTTP/WebDAV behavior, mount flags, directory/file modes, paths, and debug bitmasks.

Important constants: filesystem type `davfs`; enforced mount flags `DAV_MOPTS` and user mount flags `DAV_USER_MOPTS`; default modes; XML namespace; utab, device, mounts, cache, index, backup directory names; cache sizing/table/refresh/delay defaults; HTTP/proxy/auth/lock/etag/cookie/precheck/compression/timeout/retry/upload/lock-refresh defaults; debug masks `DAV_DBG_CONFIG`, `DAV_DBG_KERNEL`, `DAV_DBG_CACHE`, `DAV_DBG_SECRETS`.

Control flow and integration: values are consumed by option parsing, `cache.c`, `kernel_interface.c`, WebDAV setup, manpage defaults, and generated config templates. FreeBSD compatibility maps Linux mount flag names to BSD equivalents.

State and persistence: constants influence persistent cache location/naming and XML namespace but hold no state themselves.

Dependencies: POSIX mode/mount macros, `config.h` platform detection, and build-time path constants from Meson.

Risks: defaults encode security posture. `nosuid` and `nodev` are always enforced; changing them has security impact. Cache timing defaults influence freshness and lost-update risk. Retry/upload defaults determine how long dirty files remain local before backup/removal. `DAV_IF_MATCH_BUG` comment/default mismatch should be verified.

Test signals: option default tests, generated config/manpage consistency checks, mount flag enforcement tests, cache refresh/upload timing tests, and platform builds for Linux/FreeBSD macro compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/davfs2/src/defaults.h -->
