# File Research: sources/local-fs/ocfs2-tools/include/o2cb/Makefile

This Makefile prepares and installs public `o2cb` headers.

Key content:
- Generates `o2cb_err.h` by copying from `libo2cb`, building it there if needed.
- Lists public headers: `o2cb.h`, nodemanager, heartbeat, and client protocol.
- Sets `HEADERS_SUBDIR = o2cb`.
- Cleans generated `o2cb_err.h`.

Integration notes:
- Public include output depends on generated error-table headers from the library build.
