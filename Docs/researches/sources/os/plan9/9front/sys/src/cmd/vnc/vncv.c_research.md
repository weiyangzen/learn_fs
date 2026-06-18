# File Research: sources/os/plan9/9front/sys/src/cmd/vnc/vncv.c

## Role

`vncv.c` is the main VNC viewer program. It connects to a VNC server, negotiates protocol/authentication, opens a Plan 9 draw window, then runs separate loops for server updates, clipboard, keyboard, and mouse.

## Startup Flow

- Parses options for autoscale, CMAP8 12-bit mode, encodings, shared mode, TLS, verbosity, key pattern, and clipboard charset.
- Builds a network address from `host[:display]`, defaulting to TCP 5900 plus display or TLS base 35729.
- Dials the server and optionally wraps the data fd with `tlsClient()`.
- Runs client handshake and auth.
- Reads initial framebuffer size, pixel format, and desktop name.
- Initializes a draw window, chooses local/remote color format, sends encoding preferences, and opens mouse input.
- Forks worker processes for reading server updates, checking snarf, and reading keyboard; the main process reads mouse events.

## Shutdown

- Global `shutdown()` hangs up/ closes connection fds and posts notes to sibling processes.
- `vnchungup()` treats protocol closure as fatal.
- `pids[]` tracks the process group created by the viewer.

## Notable Limitations And Risk Areas

- TLS certificate verification is noted as a TODO and not enforced.
- `netmkvncaddr()` mutates the input server string when parsing `:display`.
- Viewer uses shared memory among worker processes, so `vnclock()` protects protocol writes.
- No reconnect behavior is implemented.
