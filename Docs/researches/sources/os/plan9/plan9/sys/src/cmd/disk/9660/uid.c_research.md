# File Research: sources/os/plan9/plan9/sys/src/cmd/disk/9660/uid.c

Appears to be an unfinished or placeholder sketch for detecting user/group database format.

It includes comments describing Plan 9 `/adm/users` and Unix `/etc/passwd`/`/etc/group` field layouts. `sniff` is written in pseudocode-style C without a return type and contains non-C statements such as “read first line of file into p;”. It attempts to split the first line on `:` and infer Plan 9 vs Unix format based on whether field 0 or field 2 is numeric. `isnumber` is the only complete function, using `strtol` and checking full consumption.

Integration points: `iso9660.h` declares `uidno`/`gidno`, but this file does not provide them. The real Unix adapter resolves numeric IDs in `unix.c`; Plan 9 adapter sets them to zero.

Risks and notes: as written, this file is not valid C. It is likely not built or is a historical stub.
