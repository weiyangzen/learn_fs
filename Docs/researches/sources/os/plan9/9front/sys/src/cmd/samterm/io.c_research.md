# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/io.c

`io.c` multiplexes samterm input sources: host protocol, mouse, keyboard, resize, and plumb/external input.

`kbdproc` puts `/dev/consctl` into raw mode and forwards `/dev/kbd` records through a channel. `kbdkey` tracks character events, key-up/down events, shift state, and the current keyboard rune.

`initio` initializes mouse, keyboard, host reader, and plumb reader. `waitforio` builds an `Alt` set over all sources, honors the `block` mask, flushes display when idle, handles resize reattachment, loads host/plumb buffers, and returns readiness bits.

`rcvchar`, `rcvstring`, and `getch` feed host-protocol parsing. `externload` and `externchar` turn plumb input into typed text. `kbdchar`, `ecankbd`, `ekbd`, and `qpeekc` provide nonblocking/blocking keyboard access.

`frscroll` is the frame-library scroll callback during selection; it updates selection endpoints while scrolling and uses `forcenter` to request host-origin changes and wait for necessary host data.

`RESIZED` reattaches to the resized window with `getwindow` and clears the resize flag.
