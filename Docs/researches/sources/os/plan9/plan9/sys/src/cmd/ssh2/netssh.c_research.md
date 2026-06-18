# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh2/netssh.c

This file implements `/net/ssh`, a synthetic 9P filesystem that exposes SSH connections and channels through Plan 9 network-file conventions.

Key behavior:
- Starts a 9P server mounted under `/net` with top-level `ssh/clone`, `ssh/ctl`, and `ssh/keys`.
- Allocates connection directories containing `clone`, `ctl`, `data`, `listen`, `local`, `remote`, `status`, and `tcp`.
- Allocates per-channel directories containing `ctl`, `data`, `listen`, `request`, `status`, and `tcp`.
- Handles client `connect`, server `accept`/`announce`/`reject`, user authentication, channel open/close, channel data, request queues, and key-confirmation mailbox traffic.
- Performs SSH id exchange, KEXINIT negotiation, cipher/MAC activation, packet reading, authentication, and established-state channel dispatch.

Important details:
- `threadmain` initializes crypto/public-key algorithms with `dh_init`, creates a key mailbox channel, daemonizes with `RFNOTEG`, and posts/mounts the service.
- `stopen`, `stread`, `stwrite`, `stflush`, and `stclunk` map 9P operations onto SSH connection/channel state.
- `reader0` is the main SSH transport state machine: `Initting`, `Negotiating`, `Authing`, and `Established`.
- Channel flow control uses receive queues plus `SSH_MSG_CHANNEL_WINDOW_ADJUST`; transmit writers sleep on `xmtrendez` when remote window is exhausted.
- Server-side password auth uses `auth_userpasswd` or `/mnt/keys`; successful auth can create a Plan 9 capability via `#¤/caphash`.
- Public-key auth and client-side signing use factotum-style RSA key records.
- Host-key verification is disabled by default via `nokeyverify`.

Filesystem relevance:
- Central: this is the `/net/ssh` filesystem service and the main bridge between SSH protocol state and Plan 9 file operations.
