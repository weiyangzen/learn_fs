# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devip.c

Implements Plan 9 network device `#I` with `/net/cs`, `/net/udp`, and `/net/tcp` style conversation directories.

Key behavior:
- Creates `udp` and `tcp` protocols with fixed maximum conversation counts.
- Exposes protocol directories, `clone`, conversation directories, and files `data`, `ctl`, `status`, `remote`, `local`, and `listen`.
- Allocates and reuses `Conv` objects with reference counts, owner, permissions, local/remote addresses, ports, state, and host socket fd.
- `ctl` accepts `connect`, `announce`, and `bind`.
- `listen` accepts on a listening socket and returns a new conversation.
- `data` reads and writes through backend `so_recv`/`so_send`.
- `cs` translates `net!host!service` into `/net/proto/clone ip!port`.

Important interfaces:
- Relies on `devip.h` backend functions for OS sockets.
- Uses Plan 9 IP helpers from `ip.h`.
- `ipdevtab` registers device character `I`.

Notable risks:
- `announce` calls `so_listen` after `setladdrport`, which creates/binds the socket; TCP listen semantics are assumed by backend.
- `ipread`/`ipwrite` call `nexterror()` after socket errors without a local `waserror` frame in those branches, relying on caller context.
- Conversation counts are small: UDP 10, TCP 30.
