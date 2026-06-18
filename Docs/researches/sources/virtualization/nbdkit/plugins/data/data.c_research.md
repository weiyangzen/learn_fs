# File Research: sources/virtualization/nbdkit/plugins/data/data.c

Top-level nbdkit data plugin implementation. It creates a writable in-memory or sparse allocator-backed virtual disk from command-line data.

Key behavior:
- Accepts exactly one of `raw=`, `base64=`, or `data=`.
- Accepts optional `size=` and `allocator=`.
- Extra parameters are collected only for `data=...` variable expansion.
- `get_ready` creates the allocator and loads the initial disk data.
- Final export size defaults to input data size unless `size=` overrides it.
- Exposes parallel read/write/zero/trim/flush/extents operations through the allocator API.

Capabilities:
- `can_multi_conn` returns true because all clients see the same allocator-backed disk.
- FUA and flush are native no-ops because data is memory-backed.
- Cache is native/no-op.
- Fast zero is advertised.
- Block size minimum is 1; preferred size comes from the allocator.

Optional features:
- `base64=` requires GnuTLS base64 decode support.
- `dump_plugin` reports base64, mlock, and zstd build support.
