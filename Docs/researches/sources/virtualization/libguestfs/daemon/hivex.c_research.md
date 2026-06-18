# File Research: sources/virtualization/libguestfs/daemon/hivex.c

Implements Windows Registry hive access through libhivex.

Important behavior:
- Optional build block under `HAVE_HIVEX`; otherwise emits optgroup unavailable stubs.
- Maintains one global `hive_h *h` per daemon/guestfs handle and closes it with a destructor.
- `do_hivex_open` converts filename via `sysroot_path` and honors optional flags: verbose, debug, write, unsafe.
- Read APIs expose root, node names, children, parents, values, keys, types, raw values, and strings.
- Write APIs commit, add/delete child nodes, and set values.
- `do_hivex_commit` manually validates optional output paths because generator lacks `OptPathname`.

Filesystem relevance: gives structured access to registry hive files inside mounted Windows guests.
