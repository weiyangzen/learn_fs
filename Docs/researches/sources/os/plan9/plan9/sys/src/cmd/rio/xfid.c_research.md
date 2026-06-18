# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/xfid.c

Read status: complete, 846 lines.

`xfid.c` maps decoded 9P requests onto `rio` window operations. It manages a pool of `Xfid` worker threads, request flushing, attach/open/close/read/write behavior, and byte-level handling for synthetic files.

`xfidattach` attaches to an existing window id or creates a new window from old `N...` or new `wctl` syntax. `xfidopen` enforces single-open rules for `consctl`, `mouse`, and readable `wctl`. `xfidclose` resets raw/hold/mouse/cursor/snarf state on close.

`xfidwrite` implements writes to `cons`, `consctl`, `cursor`, `label`, `mouse`, `snarf`, `wdir`, `kbdin`, and `wctl`. It handles partial UTF runes for console writes and appends snarf data until close commits it.

`xfidread` implements reads from `cons`, `label`, `mouse`, `snarf`, `text`, `wdir`, `winid`, `winname`, `window`, `screen`, and `wctl`. Image reads return a textual header followed by raw image bytes. Long-running reads support 9P flush via `flushtag` and per-request channels.

Filesystem relevance: direct implementation of most file read/write semantics in `rio`’s synthetic namespace.
