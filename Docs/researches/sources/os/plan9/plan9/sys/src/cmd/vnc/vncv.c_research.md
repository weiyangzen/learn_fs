# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/vncv.c

This is the Plan 9 VNC viewer entry point. It dials a VNC server, negotiates auth/session setup, opens a draw window, and starts concurrent server-read, snarf, keyboard, and mouse loops.

Command-line behavior:
- `-c` requests 12-bit pixel conversion mode via `bpp12`.
- `-e` overrides preferred encoding list, defaulting to `copyrect hextile corre rre raw mousewarp`.
- `-s` requests a shared VNC session.
- `-t` enables TLS and changes the default port base from 5900 to 35729.
- `-v` enables verbose logging.
- `-k` supplies an auth key pattern.

Network/session flow:
- `netmkvncaddr` parses `host[:n]`, applies display number to the base port, and returns a Plan 9 network address.
- Dials via `dial`; TLS mode wraps the fd with `tlsClient`.
- Initializes the common VNC state with `vncinit`.
- Performs client handshake/auth with `vnchandshake` and `vncauth`.
- `vncstart` sends the shared flag, then reads server dimensions, pixel format, and desktop name.

UI/process flow:
- Calls `initdraw`, enables display locking, computes desired window size including border, chooses color translation, sends encoding preferences, and opens mouse device.
- Registers `shutdown` with `atexit`; shutdown hangs up network fds and posts `die vnc kin` to sibling procs.
- Forks:
  - Server reader: `readfromserver(vnc)`.
  - Snarf watcher: `checksnarf(vnc)`.
  - Keyboard reader if `/dev/snarf` exists: `readkbd(vnc)`.
- Main process runs `readmouse(vnc)`.

Important globals:
- `encodings`, `bpp12`, `shared`, `verbose`, `vnc`, `mousefd`, and `tls` are shared with viewer helper files.

Notable risks:
- TLS client path has an explicit `XXX check thumbprint`; server certificate validation is not implemented here.
- `pids[3]` is assigned after the conditional keyboard fork; if `/dev/snarf` is absent, `p` may retain an old value from the prior fork path.
