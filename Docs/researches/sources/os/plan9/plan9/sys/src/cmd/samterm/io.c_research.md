# File Research: sources/os/plan9/plan9/sys/src/cmd/samterm/io.c

Multiplexes terminal input from host, keyboard, mouse, plumb, external-load, and resize sources.

Key responsibilities:
- `initio` initializes mouse/keyboard controls, starts the host reader, and starts plumb or external-load support.
- `waitforio` uses Plan 9 `Alt` over resource channels and control channels.
- `rcvchar`, `rcvstring`, and `getch` expose host bytes to message parsing.
- `externload` and `externchar` feed plumb/external text into normal keyboard typing.
- `ecankbd`, `ekbd`, `kbdchar`, and `qpeekc` manage keyboard lookahead.
- `RESIZED` reattaches to the resized window.

Behavior notes:
- `got` is a bitmask over `RHost`, `RKeyboard`, `RMouse`, `RPlumb`, and `RResize`.
- `block` can suppress keyboard/plumb while host reads are required.
- Host and plumb buffers are double-buffered through `hostbuf` and `plumbbuf`.
