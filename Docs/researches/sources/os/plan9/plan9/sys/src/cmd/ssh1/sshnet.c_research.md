# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/sshnet.c

SSH1-backed synthetic `/net`-style filesystem for remote TCP forwarding.

Key responsibilities:
- Authenticates an SSH1 session and starts a remote shell to enable port-open channels.
- Mounts a lib9p filesystem exposing `/`, `cs`, `tcp`, `tcp/clone`, and per-connection `ctl`, `data`, `local`, `remote`, `status`.
- Maps Plan 9 network control writes to SSH1 `SSH_MSG_PORT_OPEN`.
- Maps reads/writes on `data` to SSH channel data.
- Translates `cs` lookups into mount-local `/net` clone paths.

Important architecture:
- `threadmain`: parses options, connects, handshakes, starts fs threads, mounts service.
- `sshreadproc`: reads SSH messages into `sshmsgchan`.
- `fsnetproc`: serializes filesystem requests, clunks, and SSH messages.
- `Client`: tracks refcount, local num, remote channel num, state, pending read requests, and queued messages.

Key filesystem handlers:
- `fswalk1`, `fsopen`, `fsread`, `fswrite`, `fsflush`, `fsdestroyfid`.
- `ctlwrite`: handles `connect host!port` and `hangup`.
- `dataread`/`datawrite`: queue reads and send channel data.
- `handlemsg`: handles channel data, EOF/close, open confirmation/failure.

Risks/quirks:
- Single serialized fs thread avoids many races but requires explicit wait channels.
- `statusread` builds a local address buffer but returns only state string.
- Uses SSH1 port-forward messages and assumes remote support.
