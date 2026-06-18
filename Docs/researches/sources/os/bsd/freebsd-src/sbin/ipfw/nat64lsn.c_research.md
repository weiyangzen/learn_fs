# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/nat64lsn.c

## Purpose
Implements `ipfw nat64lsn` command handling for large-scale stateful NAT64 instances.

## Main Responsibilities
- Handles create/config/destroy/list/show/stats for NAT64 LSN.
- Supports `list states` in addition to configuration listing.
- Parses IPv4/IPv6 prefixes, queue lengths, aging timers, state chunk counts, and feature flags.
- Fetches detailed runtime statistics and prints state table entries.

## Key Implementation Details
- Create defaults include:
  - `prefix6 64:ff9b::/96`
  - `max_ports NAT64LSN_MAX_PORTS`
  - queue length `NAT64LSN_JMAXLEN`
  - default host, portgroup, TCP, UDP, and ICMP aging values.
- `prefix4` is required on create.
- `nat64lsn_parse_prefix()` duplicates and splits the prefix string, validates family-specific prefix length, masks the prefix, and stores the length.
- `nat64lsn_apply_mask()` applies IPv4 or IPv6 prefix masks before sending config to kernel.
- `max_ports` remains accepted for old configuration compatibility but is otherwise marked unused in the command table.
- Config changes are restricted to mutable parameters; prefix changes are rejected through the default error path.
- `nat64lsn_print_states()` decodes paged `ipfw_nat64lsn_stg_v1` and `ipfw_nat64lsn_state_v1` records, printing IPv6 host, alias IPv4, protocol, flags, idle age, and destination.

## Kernel/Userland Interface
Uses:
- `IP_FW_NAT64LSN_CREATE`
- `IP_FW_NAT64LSN_CONFIG`
- `IP_FW_NAT64LSN_DESTROY`
- `IP_FW_NAT64LSN_STATS`
- `IP_FW_NAT64LSN_RESET_STATS`
- `IP_FW_NAT64LSN_LIST`
- `IP_FW_NAT64LSN_LIST_STATES`

## Output Behavior
- `show` prints config, including non-default timers when verbose or changed.
- `stats` prints packet, fragment, route, memory, job queue, host, portgroup, and state counters.
- `list states` pages through kernel state chunks until sentinel index `0xFF`.

## Notable Edge Cases
- IPv6 prefix length is limited to `<= 96`.
- `set != 0` filtering in `nat64lsn_states_cb()` means explicit set filtering is slightly different from files using `g_co.use_set`.
- State-dump buffer is fixed at 4096 bytes per request and reset between pages.
