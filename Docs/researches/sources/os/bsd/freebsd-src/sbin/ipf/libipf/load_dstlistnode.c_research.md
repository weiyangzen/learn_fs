# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_dstlistnode.c

Destination-list node add/delete helper.

Key behavior:
- Allocates a `frdest_t` plus optional interface-name payload.
- Copies address, type, name offset/length, and appended name bytes.
- Uses `SIOCLOOKUPADDNODE` or `SIOCLOOKUPDELNODE` depending on `OPT_REMOVE`.

Research notes:
- Allocation size uses `sizeof(*dst) + node->ipfd_dest.fd_name`; negative `fd_name` values are handled for `op.iplo_size` but still influence allocation size.
