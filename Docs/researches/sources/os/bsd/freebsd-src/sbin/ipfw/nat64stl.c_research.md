# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/nat64stl.c

## Purpose
Implements `ipfw nat64stl` support for stateless NAT64 translation instances backed by IPv4 and IPv6 ipfw tables.

## Main Responsibilities
- Handles `create`, `config`, `destroy`, `list`/`show`, and `stats [reset]`.
- Validates NAT64 prefixes via shared `ipfw_check_nat64prefix()`.
- Requires `table4`, `table6`, and `prefix6` at create time.
- Supports flags `log` and `allow_private`.
- Retrieves and displays stateless NAT64 counters.

## Key Implementation Details
- Provides `ipfw_check_nat64prefix()`, shared by NAT64 CLAT/LSN code.
- Rejects inappropriate NAT64 prefixes such as multicast, unspecified, loopback, invalid prefix lengths, and well-known prefix with non-96 length.
- Uses `table_fill_ntlv()` to encode table references for `table4` and `table6`.
- Default `prefix6` is `64:ff9b::/96`.
- Config-time table and prefix changes are compiled out under `#if 0`; only flags can be changed.

## Kernel/Userland Interface
Uses:
- `IP_FW_NAT64STL_CREATE`
- `IP_FW_NAT64STL_CONFIG`
- `IP_FW_NAT64STL_DESTROY`
- `IP_FW_NAT64STL_STATS`
- `IP_FW_NAT64STL_RESET_STATS`
- `IP_FW_NAT64STL_LIST`

## Output Behavior
`show` prints instance name, table names, prefix, and optional flags.

## Notable Edge Cases
- Prefix parser requires explicit `/length`.
- `all` is accepted only for destroy and list.
- The source comment notes one prefix validation check “looks incorrect,” highlighting a potential historical concern around prefix filtering.
