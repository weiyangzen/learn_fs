# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/tables.c

## Purpose
Implements userland handling for in-kernel `ipfw table` objects, including creation, mutation, lookup, listing, information display, algorithm listing, and value listing.

## Main Responsibilities
- Handles table commands:
  - `add`
  - `delete`
  - `create`
  - `destroy`
  - `flush`
  - `modify`
  - `swap`
  - `info`
  - `detail`
  - `list`
  - `lookup`
  - `atomic add`
  - `lock`
  - `unlock`
- Parses table types: address, MAC, interface, number, and flow.
- Parses table value masks: legacy, skipto, pipe, fib, nat, dscp, tag, divert, netgraph, limit, IPv4 next-hop, IPv6 next-hop, and mark.
- Supports bulk entry add/delete and per-entry result reporting.
- Supports compatibility auto-create for legacy add operations into nonexistent tables.
- Fetches and prints table algorithm metadata and shared value metadata.

## Key Implementation Details
- `ipfw_table_handler()` centralizes command dispatch and validates whether `all` is legal for the selected operation.
- `table_create()` supports `type`, `valtype`, `algo`, `limit`, `locked`, `missing`, and `or-flush`.
- Default algorithms preserve compatibility:
  - `addr:radix`
  - `flow:hash`
  - `iface:array`
  - `number:array`
- `table_parse_type()` supports flow suboptions such as `src-ip`, `proto`, `src-port`, `dst-ip`, and `dst-port`.
- `table_do_modify_record()` serializes one or many `ipfw_obj_tentry` records under an `ipfw_obj_ctlv`; atomic operations set `IPFW_CTF_ATOMIC`.
- `tentry_fill_key_type()` parses keys for all supported table types, including IPv4/IPv6 CIDR, MAC masks, interface names, numbers, and flow tuple fields.
- `guess_key_type()` preserves legacy behavior and dry-run behavior by inferring table type from the key.
- `tentry_fill_value()` parses legacy values and typed values, including DSCP names, IPv4/IPv6 next-hop addresses, and hexadecimal marks.
- `table_show_entry()` formats entries according to table type and value mask.
- `tables_foreach()` fetches all tables, sorts them by numeric-aware table name, and filters by active set when needed.

## Kernel/Userland Interface
Uses:
- `IP_FW_TABLE_XCREATE`
- `IP_FW_TABLE_XMODIFY`
- `IP_FW_TABLE_XDESTROY`
- `IP_FW_TABLE_XFLUSH`
- `IP_FW_TABLE_XSWAP`
- `IP_FW_TABLE_XINFO`
- `IP_FW_TABLE_XADD`
- `IP_FW_TABLE_XDEL`
- `IP_FW_TABLE_XFIND`
- `IP_FW_TABLES_XLIST`
- `IP_FW_TABLE_XLIST`
- `IP_FW_TABLES_ALIST`
- `IP_FW_TABLE_VLIST`

## Output Behavior
- `info` prints table identity, type, refs, value type, algorithm, item count, size, and optional limit.
- `detail` adds algorithm class details, item sizes, and per-AF metadata when available.
- `list` prints entries and optionally table headers for `all`.
- Add/delete operations print per-entry status unless quiet behavior suppresses expected duplicate/not-found cases.

## Notable Edge Cases
- `atomic` is only accepted with `add`.
- `table swap` translates `EINVAL` and `EFBIG` into user-facing type/limit messages.
- Locked tables cause mutations to report `table is locked`.
- Legacy auto-create is deliberately warned as deprecated unless quiet.
- IPv4 strings accepted by `inet_aton()` but not `inet_pton()` can be rejected during type guessing.
