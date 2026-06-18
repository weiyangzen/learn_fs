# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hastd.c

Read completely: 1337 lines.

This is the top-level HAST daemon process. It parses command-line options, loads the GEOM Gate kernel module, parses configuration, opens pid/control/listen sockets, daemonizes when requested, handles synchronous signal processing, accepts peer connections, and supervises per-resource worker children.

Key responsibilities:
- Maintains global daemon state: `cfgpath`, parsed `cfg`, pidfile handle, foreground/debug mode, and termination state.
- Starts listening on the configured control socket and all HAST peer listen addresses.
- Accepts remote HAST connections and performs the two-step secondary-side handshake using resource name, protocol version, and per-session token.
- Spawns/restarts primary workers and invokes secondary workers when both incoming and outgoing peer connections are established.
- Handles SIGHUP reloads by parsing a new config, switching listen/control sockets, adding/removing resources, restarting resources when required, and live-reloading compatible primary settings.
- Uses socketpair protocol connections for parent/child control, event, and connection-migration channels.
- Cleans descriptors aggressively in worker children and asserts that only expected descriptors remain open.

Important interactions:
- Uses `yy_config_parse()`/`yy_config_free()` from `parse.y`.
- Uses `proto_*` for TCP/socketpair abstractions, `hast_proto_*` for NV-framed HAST messages, and `control_*`/`event_*` for local daemon control.
- Calls `hastd_primary()` and `hastd_secondary()` to transfer resource work into role-specific workers.
- Uses hooks (`hook_init`, `hook_check`, `hook_fini`) for external event execution and `pjdlog` for daemon/syslog output.

Reliability and security notes:
- Peer admission first checks whether the remote address matches any configured resource, then verifies the requested resource and token.
- Reload distinguishes changes requiring full restart from changes safe for primary worker live reload.
- `select()` is bounded by `FD_SETSIZE`; many resources/listeners can hit the explicit assertion.
- Descriptor cleanup is intentionally strict and aborts if unexpected descriptors remain in children, which helps prevent fd leaks across privilege boundaries.
