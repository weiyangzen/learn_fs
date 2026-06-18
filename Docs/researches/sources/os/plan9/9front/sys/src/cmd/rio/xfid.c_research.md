# File Research: sources/os/plan9/9front/sys/src/cmd/rio/xfid.c

`xfid.c` implements rio's per-request 9P file operation workers. It maps file server operations onto window state and global rio devices, including `/dev/cons`, `/dev/text`, `/dev/mouse`, `/dev/kbd`, `/dev/wctl`, `/dev/snarf`, `/dev/window`, `/dev/screen`, labels, cursor data, working directory, winid, winname, and tap channels.

`xfidinit`, `xfidallocthread`, and `xfidctl` maintain a reusable pool of `Xfid` request workers. Each worker receives a handler function, sets `flushtag`, runs the operation, then decrements its refcount and returns to the free list.

`xfidflush` synchronizes Plan 9 flush requests with in-flight workers. It locates the matching old tag, arranges cancellation via `flushc`, releases the file server flush gate, and either cancels or responds to the flush.

`xfidattach` interprets attach names for existing window IDs, `none`, legacy `N...` geometry, and `new...` wctl-style window creation. It validates rectangles, allocates visible or hidden images, and binds the Fid to a `Window`.

Open/close manage single-open state for control, keyboard, mouse, wctl, and tap files. Closing `Qconsctl` drops raw/hold mode; closing `Qmouse` refreshes the window; closing writable `Qsnarf` converts temporary bytes into the global rune snarf buffer.

`xfidwrite` handles text/cons writes with UTF partial-rune carry, consctl commands (`holdon/off`, `rawon/off`), cursor binary data, label replacement, synthetic mouse movement, snarf append, window directory changes, wctl commands, and tap forwarding.

`xfidread` services blocking cons/kbd/mouse/wctl reads through window channels with flush/deletion races, and simple reads for label, snarf, text, wdir, winid, winname, image headers/pixels, and screen pixels. `readwindow` handles offset reads from image data.
