# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/daemon/remote.h

Unbound daemon header for remote-control support and fast reload plumbing.

Core structures:
- `struct rc_state`: active remote-control connection state, commpoint, handshake state, optional SSL handle, fd, and owning remote controller.
- `struct daemon_remote`: remote-control listener state, worker, accept list, certificate mode, active/max-active counters, busy list, and optional SSL context.
- `struct remote_stream`: SSL-or-plain output stream.
- `enum fast_reload_notification`: protocol between fast reload thread and server thread.
- `struct fast_reload_printq`: queued output for a remote-control client during fast reload.
- `struct fast_reload_auth_change`: tracks auth-zone add/delete/change during reload.
- `struct fast_reload_thread`: thread, socketpairs, output queue, locks, auth-zone change state, and reload coordination flags.

API:
- create/delete/clear remote control state.
- open/listen/stop/start remote-control ports.
- execute remote commands.
- SSL printing/line-reading helpers when SSL is available.
- start/stop fast reload thread.
- fast reload callbacks and worker pickup.

Role in group:
- Declares Unbound remote-control machinery. In this OpenBSD build, SSL support is compiled in, but `unwind` does not expose the full upstream daemon control surface in the frontend file read here.
