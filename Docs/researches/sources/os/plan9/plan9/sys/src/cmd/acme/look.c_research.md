# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/look.c

This file implements button-3 look/open/search behavior, plumber integration, filename expansion, and window lookup.

Key behavior:
- `look3()` expands clicked text, notifies external event clients, tries plumber send, then opens files or searches text.
- `plumblook()` opens files from plumber messages with optional address attributes.
- `plumbshow()` creates a new window containing supplied plumber data.
- `search()` performs wraparound literal rune search in a text.
- `expandfile()` recognizes file names and optional `:addr` suffixes, including include-file syntax `<name>`.
- `dirname()` resolves relative names against a window tag path.
- `openfile()` reuses an existing window or creates/loads a new one and jumps to an address.
- `new()` implements the `New` built-in for unnamed or named windows.

Important details:
- External event clients receive pre- and post-expansion look events.
- File recognition checks existing Acme windows first, then `access()`.
- Include resolution checks window include dirs, `/sys/include`, and `/$objtype/include`.
- Directory names are normalized with `cleanname`.

Filesystem relevance:
- High: resolves paths, opens files/directories into Acme windows, and integrates plumber file messages.
