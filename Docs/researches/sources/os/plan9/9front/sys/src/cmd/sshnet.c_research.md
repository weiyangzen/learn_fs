# File Research: sources/os/plan9/9front/sys/src/cmd/sshnet.c

`sshnet.c` exposes a remote SSH TCP forwarding session as a Plan 9 `/net`-style filesystem.

Filesystem model:
- Serves root entries `cs` and `tcp`.
- Under `tcp`, exposes `clone` and per-client numbered directories.
- Per-client files include `ctl`, `data`, `local`, `remote`, `status`, and `listen`.
- Qid path encodes entry type and client number with `PATH`, `TYPE`, and `NUM`.

Client/protocol state:
- `Client` tracks local/remote endpoints, state (`Closed`, `Dialing`, `Listen`, `Established`, `Teardown`, `Finished`), SSH channel ids, windows, packet limits, queued 9P read/write requests, and queued incoming data messages.
- `Msg` is a bounded SSH packet/message buffer.
- `pack`/`unpack` encode SSH channel/global request messages.

Operations:
- `ctlwrite connect host!port` opens SSH `direct-tcpip`.
- `ctlwrite announce host!port` sends `tcpip-forward`; `listen` waits for incoming `forwarded-tcpip`.
- `cswrite` translates `tcp!host!service` into `/net/tcp/clone host!port`, using `/lib/ndb/common`; `!`-prefixed writes delegate to a real `/net/cs`.
- `dataread` and `datawrite` bridge 9P reads/writes to SSH channel data with window accounting.
- `handlemsg` handles SSH channel open confirmation/failure, remote open, data, window adjust, EOF, and close.

Startup:
- Spawns `/bin/ssh -X ...`, opens a dummy session channel to confirm the mux is live, then posts/mounts the 9P service.

Risks:
- Single event loop serializes fs requests and SSH messages, simplifying state but making blocking mistakes costly.
- Flow control depends on correct send/receive window bookkeeping.
- Only TCP forwarding semantics are represented; unsupported channel open types are rejected.
