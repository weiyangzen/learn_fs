# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/wsys.c

This file handles the Plan 9 window-system integration for the VNC viewer: resizing, cursor setup, mouse event forwarding, mouse warp, and snarf synchronization.

Window resize:
- `resize(Vnc*, int first)` calls `getwindow`, computes the server image size plus borders, and writes `/dev/wctl` resize commands when first opened or when the window is larger than the VNC desktop.
- `eresized` resizes and requests a full framebuffer update.

Mouse handling:
- Defines a small dot cursor and writes it to the draw device cursor file.
- `initmouse` opens the display device's mouse file as `ORDWR`.
- `readmouse` reads fixed-size Plan 9 mouse events, handles resize messages, subtracts `screen->r.min` to produce VNC-relative coordinates, clips to the VNC desktop, and sends `MMouse` messages.
- Mouse wheel buttons are sent as press followed by synthetic release for non-button-1/2/3 bits.
- `mousewarp` writes an `mX Y` command to the mouse fd after converting VNC-relative coordinates to screen coordinates.

Clipboard/snarf:
- `writesnarf` receives VNC clipboard bytes from the network and writes them to `/dev/snarf`, incrementing local `snarfvers`.
- `getsnarf` reads the entire local snarf file into a dynamically grown buffer.
- `checksnarf` polls `/dev/snarf` once per second, compares `qid.vers`, and sends `MCCut` to the server when local snarf changes.

Notable risks:
- `getsnarf` reallocates without checking for failure.
- Snarf polling is coarse and relies on qid version changes.
- Clipboard reads can grow unbounded except by available memory.
