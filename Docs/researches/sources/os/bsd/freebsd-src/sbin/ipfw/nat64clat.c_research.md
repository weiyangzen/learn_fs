# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/nat64clat.c

## Purpose
Implements `ipfw nat64clat` command handling for CLAT-side NAT64 translation instances.

## Main Responsibilities
- Handles `create`, `config`, `destroy`, `list`/`show`, and `stats [reset]`.
- Requires instance names unless operating on `all` for destroy/list.
- Parses and validates CLAT and PLAT IPv6 prefixes.
- Supports flags `log`/`-log` and `allow_private`/`-allow_private`.
- Retrieves and prints NAT64 CLAT statistics.

## Key Implementation Details
- Defaults PLAT prefix to `64:ff9b::/96` on create.
- Requires `clat_prefix`; `plat_prefix` is also tracked as a required create field though it has a default.
- Prefix validation is delegated to shared `ipfw_check_nat64prefix()`.
- Existing config is fetched before mutation in `nat64clat_config()`, then updated and written back.
- `nat64clat_foreach()` dynamically resizes list buffers on `ENOMEM`, then optionally sorts by set and numeric-aware name comparison.

## Kernel/Userland Interface
Uses:
- `IP_FW_NAT64CLAT_CREATE`
- `IP_FW_NAT64CLAT_CONFIG`
- `IP_FW_NAT64CLAT_DESTROY`
- `IP_FW_NAT64CLAT_STATS`
- `IP_FW_NAT64CLAT_RESET_STATS`
- `IP_FW_NAT64CLAT_LIST`

## Output Behavior
`nat64clat_show_cb()` prints:
- optional `set N`
- instance name
- `clat_prefix`
- `plat_prefix`
- optional `log`
- optional `allow_private`

## Notable Edge Cases
- `all` is accepted only for `destroy` and `list`/`show`.
- `config` requires at least one option.
- Prefix arguments to `config` must include `/length`; create parsing assumes a slash is present when converting length.
