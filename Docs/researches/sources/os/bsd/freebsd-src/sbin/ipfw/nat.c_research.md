# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/nat.c

## Purpose
Implements the `ipfw nat` userland command support for in-kernel IPv4 NAT44 configuration, deletion, listing, and log/config display.

## Main Responsibilities
- Parses `ipfw nat <id> config ...` options into `struct nat44_cfg_nat` plus variable-length redirect payloads.
- Supports NAT address selection by static IPv4 address or dynamic interface address.
- Handles NAT flags such as `log`, `deny_in`, `same_ports`, `unreg_only`, `unreg_cgn`, `skip_global`, `reset`, `reverse`, `proxy_only`, and `udp_eim`.
- Parses `redirect_addr`, `redirect_port`, and `redirect_proto` rules, including LSNAT-style server pools.
- Implements NAT instance deletion with `IP_FW_NAT44_DESTROY`.
- Lists NAT instances and fetches either configuration or log data with `IP_FW_NAT44_LIST_NAT`, `IP_FW_NAT44_XGETCONFIG`, and `IP_FW_NAT44_XGETLOG`.

## Key Implementation Details
- `set_addr_dynamic()` walks routing interface sysctl data using `NET_RT_IFLIST` to find an interface by name and capture its first IPv4 address.
- Redirect parsing uses helpers inherited from `natd.c` style logic:
  - `StrToAddr()`
  - `StrToPortRange()`
  - `StrToProto()`
  - `StrToAddrAndPortRange()`
- Redirect records are packed into a single contiguous buffer after `ipfw_obj_header` and `nat44_cfg_nat`.
- `estimate_redir_addr()` and `estimate_redir_port()` pre-compute variable payload size before allocation.
- `setup_redir_port()` enforces equal local/public port range sizes and special SCTP constraints where target port remapping is not allowed.
- `nat_port_alias_parse()` validates `port_range` values as privileged-excluding ranges from 1024 through 65535.
- `nat_show_cfg()` mutates the local fetched copy of `n->mode` while printing flags, which is safe because fetched data is temporary display data.

## Kernel/Userland Interface
Uses `do_set3()` and `do_get3()` wrappers around ipfw socket operations:
- `IP_FW_NAT44_XCONFIG`
- `IP_FW_NAT44_DESTROY`
- `IP_FW_NAT44_LIST_NAT`
- `IP_FW_NAT44_XGETCONFIG`
- `IP_FW_NAT44_XGETLOG`

## Notable Edge Cases
- NAT ID must be numeric and greater than zero.
- `same_ports` and `port_range` are mutually exclusive.
- Optional redirect arguments are detected by checking whether the next token begins with a digit, so hostname-style optional addresses are not accepted in those positions.
- Dynamic interface NAT falls back to `INADDR_ANY` when the interface exists but has no IPv4 address.
