# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getprotobynumber_r.c

Read completely: 66 lines.

This file implements `getprotobynumber_r`. It opens/rewinds the protocol database, iterates entries with `getprotoent_r`, and returns the first entry whose `p_proto` equals the requested protocol number.

If `stayopen` is false, it closes the backing file before returning.

Security/reliability notes: simple linear scan; caller-provided `protoent_data` owns the parse buffers.
