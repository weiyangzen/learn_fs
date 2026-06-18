# File Research: sources/os/plan9/9front/sys/src/cmd/aux/wacom.c

Implements a Plan 9 9P service that exposes a serial Wacom tablet as `/dev/tablet`.

Key responsibilities:
- Opens `/dev/eia2`, configures serial speed to 19200 baud, queries tablet capabilities, and reads screen size from `/dev/draw/new`.
- Parses Wacom packets into scaled x/y coordinates, button bits, and pressure.
- Formats events as `m x y buttons pressure\n`.
- Maintains per-reader queues and pending read requests.
- Broadcasts each tablet event to all open readers.
- Mounts a synthetic 9P service after forking background service processes.

Important interfaces:
- Uses `thread.h`/`9p.h` `Srv`, `Req`, `Fid`, `File`, and `alloctree/createfile`.
- Uses Plan 9 `Ref` for message reference counting and `Lock` for queue/reader protection.

Notes:
- `readpacket` scales raw tablet coordinates/pressure using queried maximums and current screen size.
- `tabletread` rejects concurrent reads on the same fid.
