# File Research: sources/virtualization/nbdkit/plugins/info/info.c

This plugin exposes small synthetic block exports containing connection or server metadata.

Modes:
- `exportname` returns the client export name.
- `base64exportname` decodes the export name as base64.
- `address` returns peer address as text.
- `time` returns current wall-clock seconds/useconds.
- `uptime` returns time since plugin load.
- `conntime` returns time since connection open.
- `version` returns the nbdkit version string.

Implementation:
- `info_load` records plugin load time.
- `info_open` constructs per-connection data depending on mode.
- Time modes allocate 12 bytes and refresh data on every read.
- Time values are packed big-endian: 8-byte seconds plus 4-byte microseconds.
- `.can_multi_conn` returns true only for stable modes.
- `.can_cache` returns native cache.

Optional dependencies:
- Base64 mode needs GnuTLS base64 decode support.
- Address mode needs `inet_ntop`.

Security considerations:
- Comments explicitly call out avoiding unbounded output, crashes, hangs, and host information leaks.
- Unix socket address mode returns only `unix`, not a filesystem path.

Risks:
- Time modes are intentionally not multi-connection safe.
- Base64 empty string is special-cased due to GnuTLS behavior.
