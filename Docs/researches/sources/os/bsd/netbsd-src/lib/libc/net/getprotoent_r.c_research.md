# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getprotoent_r.c

Read completely: 152 lines.

This file implements reentrant protocol database iteration: `setprotoent_r`, `endprotoent_r`, and `getprotoent_r`.

It opens `_PATH_PROTOCOLS`, reads entries with `fparseln`, parses protocol name, number, and aliases, and grows the alias pointer array with `reallocarr` as needed. `endprotoent_r` closes the file and frees the line and alias buffers held in `protoent_data`.

Security/reliability notes: `reallocarr` protects alias-array size multiplication. Parsed strings point into `pd->line`, so they remain valid only until the next call that replaces that line or until `endprotoent_r`.
