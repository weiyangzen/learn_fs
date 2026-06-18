# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/net.c

User-mode network transport for 9P messages over Plan 9 network connections.

Key data:
- `Network` tracks listener state for an announce string.
- `Netconn` is per remote address/channel allocation state and reply queue pointer.
- `Conn9p` is per accepted connection fd, with ref count, remote address, and backpointer to `Netconn`.

Key responsibilities:
- `netinit()` announces configured addresses (`annstrs`, default `tcp!*!9fs`).
- `netstart()` starts one network output process and one input listener per configured network.
- `neti()` accepts connections and forks `connection()` processes.
- `connection()` reads 9P messages from one fd, allocates `Msgbuf`s, assigns channel/protocol metadata, and sends to `serveq`.
- `neto()` receives reply `Msgbuf`s from `netoq` and writes them back to the original connection fd.
- `getchan()` reuses or allocates a `Chan` for a remote address, sets send/reply queues and channel metadata.
- `nethangup()` and `chanhangup()` tear down channels/connections and free active fids.
- `size9pmsg()` and `readalloc9pmsg()` frame 9P2000-style messages by 32-bit length.

Important interactions:
- Uses `fs_chaninit`, `fileinit`, `mballoc`, `mbfree`, `fs_send`, `fs_recv`.
- Relies on `Msgbuf.param` to carry `Conn9p*` for replies.
- Uses `getnetconninfo()` to discover remote address.

Research notes:
- The file comments document a major architecture shift from kernel Ethernet/IL packet processing to user-mode per-connection stream processing.
- Connections are grouped by remote address when choosing a `Chan`, which can multiplex sessions from the same caller.
- `Conn9p` references are incremented for both live connection and in-flight packets, then decremented in output.
