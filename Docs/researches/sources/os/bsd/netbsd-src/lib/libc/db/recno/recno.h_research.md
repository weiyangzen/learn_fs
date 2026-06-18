# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/recno.h

Small recno private header. It defines `enum SRCHOP` with `SDELETE`, `SINSERT`, and `SEARCH`, controlling whether `__rec_search` adjusts internal record counts while descending. It then includes the shared btree internals and recno private prototypes.

Dependencies: `../btree/btree.h` and `recno/extern.h`.

Risks/invariants: inclusion pulls in the full btree private API, reflecting that recno is implemented as a specialized btree rather than an independent access method.
