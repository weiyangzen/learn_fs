# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/vncs.c

This is the Plan 9 VNC server. It starts a private Plan 9 draw/mouse/console environment, runs a command inside it, announces a VNC service, accepts clients, and exports the screen with dirty-rectangle updates.

Startup flow:
- Parses options for TLS cert, display number, geometry, pixel channel, kill mode, verbosity, and alternate network mount.
- `-k :display` locates the server's TCP control file and writes `hangup`.
- Daemonizes with `rfork`, allocates per-process private data with `privalloc`, initializes the compatibility/screen layer, exports draw/mouse/cons devices, rebuilds `/dev`, and starts the target command, defaulting to interactive `/bin/rc`.
- Announces TCP on `baseport + display`; default base is `5900`, TLS mode uses `35729`.
- Accept loop creates a `Vncs`, links it into the global `clients` list under `clients.QLock`, fills remote/netpath metadata, and calls `vncaccept`.

Client lifecycle:
- `vncaccept` forks per connection and optionally wraps the data fd in TLS with `tlsServer`.
- Performs VNC server handshake/auth via `vncsrvhandshake` and `vncsrvauth`.
- Reads the shared flag; if not shared, `killclients` hangs up existing clients.
- Sends server init: dimensions, pixel format converted from `gscreen->chan`, and desktop name `Plan9 Desktop`.
- Forks reader and writer loops sharing memory.
- Per-process `atexit(exiting)` drives `vncclose`, which removes the client from the global list and frees resources only after both client procs have exited.

Client read path:
- `clientreadproc` consumes client-to-server messages.
- `MPixFmt` installs client pixel format once and derives a Plan 9 image channel via `fmt2chan`.
- `MSetEnc` records the first supported encoding callback pair from raw/RRE/CoRRE/hextile and optional copyrect/mousewarp support.
- `MFrameReq` marks update demand and adds full requested rectangles for non-incremental requests.
- `MKey` forwards keyboard events to `vncputc`.
- `MMouse` forwards mouse state to `mousetrack`.
- `MCCut` receives client clipboard text and updates Plan 9 snarf state.

Client write path:
- `clientwriteproc` allocates/reallocates a per-client `Memimage` in the requested channel, sends snarf updates, and calls `updateimage` when an update has been requested.
- `updateimage` snapshots dirty rectangles from `v->rlist`, handles cursor redraw damage, copies changed screen pixels from `gscreen` into the client image, counts encoded rectangles, sends `MFrameUpdate`, and optionally emits a mouse-warp pseudo-rectangle.
- It carefully drops the client lock and draw lock during expensive or blocking phases.

Global update integration:
- `flushmemscreen(Rectangle)` clips screen damage to `gscreen->r` and appends it to every client's rectangle list.
- `mousewarpnote(Point)` marks `needwarp` for clients that advertised `EncMouseWarp`.

Pixel format conversion:
- `fmt2chan` converts VNC RGB masks/shifts to a Plan 9 channel descriptor, adding one ignore channel if bpp exceeds RGB depth.
- `chan2fmt` converts a Plan 9 channel descriptor into VNC max/shift fields.

Shutdown behavior:
- `killall` posts a hangup to the command process group, closes service/export fds, and posts `die vnc kin` to its own process group.
- `shutdown` is registered with `atexit`; `noteshutdown` handles external notes.

Notable risks and quirks:
- Several comments state pixel format and encoding changes are effectively one-shot because supporting later changes would need more locking and image lifetime management.
- `fmt2chan` assumes at most one contiguous run of ignored bits.
- TLS mode reads a certificate and wraps the connection but this file does not perform client authentication.
- Shared global `shared` is overwritten per connecting client, so it is not a per-client setting despite client-specific semantics.
