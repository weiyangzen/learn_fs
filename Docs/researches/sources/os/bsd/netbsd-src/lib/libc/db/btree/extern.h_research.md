# File Research: sources/os/bsd/netbsd-src/lib/libc/db/btree/extern.h

Declares the private btree/recno-shared implementation interface. It lists btree close, get, put, delete, sequence, sync, file-descriptor, comparison, return, search, split, page allocation/free/relink, byte-swap filters, and overflow helpers.

The exported private functions connect the public `DB` methods installed by `__bt_open` and `__rec_open` to lower-level page manipulation. The overflow declarations (`__ovfl_delete`, `__ovfl_get`, `__ovfl_put`) are shared by btree leaf data, internal separator preservation, and recno record payloads.

Conditional declarations provide debug dump and statistics entry points when `DEBUG` or `STATISTICS` is enabled.

Dependencies: included from `btree.h`, and assumes `BTREE`, `DB`, `DBT`, `EPG`, `PAGE`, and page-number types have already been defined.

Risks/invariants: this is not a public API; prototypes expose tightly coupled page-cache and tree internals, so signature changes ripple through btree and recno code.
