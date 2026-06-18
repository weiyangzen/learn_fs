# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getprotobyname_r.c

Read completely: 77 lines.

This file implements `getprotobyname_r`. It opens/rewinds the protocol database through `setprotoent_r`, iterates `getprotoent_r`, and matches the requested name against `p_name` and aliases.

If `stayopen` is not set, it closes the protocol file before returning.

Security/reliability notes: caller owns the `protoent` and `protoent_data` storage. Matching is case-sensitive, mirroring the historical implementation.
