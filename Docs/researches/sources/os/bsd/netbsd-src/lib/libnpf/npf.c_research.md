# File Research: sources/os/bsd/netbsd-src/lib/libnpf/npf.c

Implements the userland `libnpf` API for constructing, importing/exporting, submitting, retrieving, and mutating NPF firewall configurations. All major objects (`nl_config`, rules, rule procedures, tables, NAT entries, extensions, ALGs) are backed by libnv `nvlist_t` dictionaries.

Important dependencies: system ioctl/stat/mmap APIs, networking headers, `nv.h`, `dnv.h`, `cdbw.h`, and `npf.h`.

Main components:
- Configuration exchange: `_npf_xfer_fd()` supports socket nvlist send/receive off-NetBSD and character/block device ioctl transfer on NetBSD-like builds, with `NPF_VERSION` validation.
- Configuration building: nested `__rules` arrays are flattened into `rules` arrays with `skip-to` markers by `_npf_rules_process()`.
- Parameters: named numeric parameters live under the `params` nvlist, with iteration support and optional defaults.
- Dynamic rulesets: add/remove/remove-by-key/flush/list operations package rule dictionaries for `IOC_NPF_RULE`.
- Rules and rprocs: constructors and setters add attributes, BPF code, priority, procedure names, binary keys/info, user/group IDs, and extension calls.
- NAT: NAT entries are rule dictionaries with NAT metadata for type, flags, address/mask, port, table, ALG, and NPTv6 adjustment.
- Tables: table entries are nvlist arrays; constant tables are converted into a CDB blob using `cdbw`, a temporary file, `mmap()`, and `nvlist_move_binary()`.
- Connections: NAT lookup and connection listing retrieve kernel state and decode addresses/ports for callbacks.
- Debug/misc: supports adding debug interface dictionaries and dumping built configs.

Notable risks: many insertion APIs transfer ownership by appending/moving nvlists and then destroying/freeing wrapper objects, so callers must not reuse inserted objects. `_npf_rules_process()` realloc failure is not checked before assigning through `p`. `npf_conn_list()` returns early without destroying `ncf` if `conn-list` is absent.
