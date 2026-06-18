# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/vncs.c

## Role

`vncs.c` is the main VNC server program. It creates a private Plan 9 desktop, exports synthetic draw/mouse/cons devices into `/dev`, launches a command inside that namespace, listens for VNC clients, and streams framebuffer updates.

## Startup Flow

1. Parses options for certificate/TLS mode, display number, geometry, pixel format, network mount point, no-auth mode, kill mode, and verbosity.
2. Backgrounds into a new process/name/fd/note context.
3. Initializes compatibility state and creates the in-memory screen.
4. Exports `draw`, `mouse`, and `cons` devices through `exporter()` and mounts them before the real `/dev`.
5. Launches a child command, defaulting to interactive `rc`, after starting and synchronizing `kbdfs`.
6. Opens `/dev/kbdin` for keyboard injection.
7. Announces a VNC TCP service and accepts clients.

## Client Lifecycle

- `vncaccept()` forks a handler per client, optionally wraps the data fd in TLS, performs handshake/auth, handles shared/non-shared policy, sends initial framebuffer dimensions and pixel format, and forks reader/writer paths.
- `clientreadproc()` processes client messages: pixel format, colormap, encoding preferences, framebuffer requests, desktop resize, key events, mouse events, and cut text.
- `clientwriteproc()` periodically sends clipboard changes and framebuffer updates when the client has outstanding update requests.
- `vncclose()`, `killclients()`, `killall()`, `shutdown()`, and note handling coordinate cleanup.

## Framebuffer Update Model

- `flushmemscreen()` adds dirty rectangles to every client.
- `updateimage()` copies dirty screen regions into the client's pixel-format image, overlays cursor when needed, sends resize pseudo-rectangles, encoded framebuffer rectangles, and mouse-warp pseudo-rectangles.
- Encoding functions are selected from raw, RRE, CoRRE, or hextile based on the client's preference list.
- Clipboard is synchronized through the shared `snarf` version.

## Pixel Format Handling

- `chan2fmt()` converts Plan 9 channels to VNC pixel format for initial server advertisement.
- `fmt2chan()` converts client-requested `Pixfmt` back into a Plan 9 channel descriptor, including ignored padding bits where possible.
- Client image buffers are recreated when size or channel changes.

## Notable Limitations And Risk Areas

- Authentication defaults to VNC challenge-response unless `-A` disables it; stronger security depends on TLS option and external certificate setup.
- Pixel format changes are effectively expected once; comments note missing locking for repeated changes.
- Shared global `shared` is assigned from each client and also used as option state.
- The private desktop and client handlers are process-shared memory via `rfork(RFMEM)`, so locks around clients, draw state, and VNC writes are essential.
- Resizing rewrites `gscreen->clipr`, redraws the console, and resets the draw screen image; active draw clients constrain resizing behavior.
