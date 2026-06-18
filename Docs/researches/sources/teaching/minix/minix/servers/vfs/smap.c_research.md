# File Research: sources/teaching/minix/minix/servers/vfs/smap.c

Maintains socket-driver mappings.

Key behavior:
- `init_smap` initializes one-based socket map numbers and clears protocol-family mappings.
- `smap_map` registers or replaces a socket driver by label, endpoint, and supported domains. It validates domains, prevents conflicts, handles stateless restarts by unsuspending old endpoint users and invalidating existing socket filps, then updates `smap` and `pfmap`.
- `smap_unmap_by_endpt` deregisters a socket driver on exit and invalidates sockets before clearing mappings.
- `smap_endpt_up` handles socket-driver restart announcements by invalidating preexisting sockets.
- `make_smap_dev` encodes the one-based smap number in the high 32 bits of `dev_t` and the driver-local socket ID in the low 32 bits.
- `get_smap_by_dev`, `get_smap_by_endpt`, and `get_smap_by_domain` decode socket device numbers and look up drivers.

Important dependencies:
- Uses `invalidate_filp_by_sock_drv` and `unsuspend_by_endpt` to clean up driver restarts.
- Consumed heavily by `sdev.c`, `socket.c`, and `select.c`.

Notable implementation details:
- Socket `dev_t` values are in a separate logical namespace from block/character device numbers; file type must be checked before interpreting them.
- Endpoint lookup is O(n), with an inline TODO noting this could be cached in `fproc`.
