# File Research: sources/virtualization/libnbd/lib/handle.c

Primary handle lifecycle and configuration implementation.

Lifecycle:
- `nbd_create`: allocates handle, assigns debug name, initializes defaults, mutex, negotiation preferences, strictness, URI policy, export name, state, and generated create event.
- `nbd_close`: runs close callbacks in two phases, frees callbacks and vectors, aborts/free command queues, tears down socket/subprocess/socket-activation temp files, frees all owned strings, destroys mutex, poisons magic, and frees handle.
- `free_cmd_list`: completes pending commands with existing error or `ENOTCONN` before freeing.

Configuration APIs:
- Handle name, close callbacks, socket activation name, private data.
- Export name, requested block size/full info/canonical name/description.
- Metadata context request list.
- Extended headers, structured replies, metadata context request toggles.
- Handshake flags, pread initialization, strict mode.
- Package/version accessors.
- Subprocess kill/PID accessors.
- Feature support probes for TLS/vsock/URI.
- URI policy setters.
- Traffic stats.
- Keepalive and TCP keepalive option storage/getters.

Interactions:
- `flags.c` reset is triggered by export-name changes and close.
- `socket.c`/`crypto.c` close through socket ops.
- Generated state machine is initialized by `cmd_create`.

Research notes:
- Defaults request extended headers, structured replies, metadata contexts, and block size information.
- Close callbacks are called before their user data is freed, allowing callbacks to share backing structs.
- Keepalive getter reads the live socket option when connected, not just the stored desired flag.
