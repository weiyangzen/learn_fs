# File Research: sources/os/bsd/openbsd-src/sbin/pfctl/pfctl_radix.c

`pfctl_radix.c` provides PF table/radix ioctl wrappers, interface ioctl wrappers, typed dynamic buffer management, and token loading for table address files. It is the low-level bridge between `pfctl` table operations and `/dev/pf` ioctls.

Primary responsibilities:
- Defines the global `pfr_ktables` RB tree and generates RB functions for parser-created table definitions.
- Implements `pfr_ktable_compare()` ordering by table name and anchor.
- Wraps table ioctls for clearing/adding/deleting/getting tables, getting/clearing table stats, clearing/adding/deleting/setting/getting/testing addresses, getting/clearing address stats, inactive-define operations, and interface listing.
- Implements typed `struct pfr_buffer` operations used throughout pfctl.
- Implements `pfr_buf_load()` to read address tokens from a file or stdin and append them as table addresses.
- Implements `pfr_next_token()` to parse whitespace-separated tokens while skipping comments.

Table/ioctl wrappers:
- Table functions prepare `struct pfioc_table`, validate pointer/size combinations, fill flags, table filters, buffer pointers, element sizes, sizes/tickets, then call the appropriate `DIOCR*` ioctl.
- `pfr_ina_define()` supports inactive transaction table definition with a ticket, used during ruleset loads.
- `pfi_get_ifaces()` wraps `DIOCIGETIFACES` for interface status display elsewhere.

Buffer handling:
- `buf_esize[]` maps each `PFRB_*` type to its element size.
- `pfr_buf_add()` grows as needed, copies one typed element, and increments size.
- `pfr_buf_next()` supports `PFRB_FOREACH()` iteration.
- `pfr_buf_grow()` allocates at least 64 entries initially or doubles capacity, using `reallocarray()` and zeroing the new region.
- `pfr_buf_clear()` frees backing memory and resets counters.

Input parsing:
- `pfr_buf_load()` opens files through `pfctl_fopen()` unless input is `-`, then repeatedly tokenizes and calls `append_addr()`.
- `pfr_next_token()` skips whitespace and `#` comments, enforces `BUF_SIZE`, and uses a static `next_ch` to preserve one-character lookahead across calls.

Integration points:
- Uses global `dev` from `pfctl.c` for all ioctl calls.
- Exposes wrappers via `pfctl.h`.
- Calls parser address conversion through `append_addr()`.
- Used by table command implementation, parser table loading, optimizer table generation, and transaction handling.

Notable risks and edge cases:
- All wrappers reject negative sizes and missing buffers for nonzero sizes with `EINVAL`.
- `pfr_clr_astats()` requires an address pointer even when size validation otherwise allows some null table cases, matching its specific ioctl semantics.
- `pfr_next_token()` has static lookahead state, so it is not reentrant and assumes sequential file loading.
- Initial buffer growth handles `pfrb_msize == 0`; callers must set a valid `pfrb_type` before using buffer operations.
