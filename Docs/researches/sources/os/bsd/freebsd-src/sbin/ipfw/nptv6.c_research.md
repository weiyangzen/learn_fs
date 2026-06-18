# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/nptv6.c

## Purpose
Implements `ipfw nptv6` command handling for IPv6 network prefix translation instances.

## Main Responsibilities
- Handles `create`, `destroy`, `list`/`show`, and `stats [reset]`.
- Parses internal prefix, external prefix or external interface, and prefix length.
- Enforces RFC 6296-style prefix length consistency.
- Supports dynamic external prefixes via interface name.
- Retrieves and prints translation statistics.

## Key Implementation Details
- `nptv6_parse_prefix()` accepts IPv6 prefixes with optional `/length`, validating lengths from 8 through 64.
- Create requires:
  - `int_prefix`
  - exactly one external source: `ext_prefix` or `ext_if`
  - `prefixlen`, either explicitly or inferred from deprecated prefix suffixes.
- If prefix lengths are embedded in `int_prefix`/`ext_prefix` without `prefixlen`, the command works but warns to use `prefixlen`.
- Internal and static external prefixes are masked with `n2mask()` and `APPLY_MASK()`.
- Dynamic external interface mode stores `if_name` and sets `NPTV6_DYNAMIC_PREFIX`.

## Kernel/Userland Interface
Uses:
- `IP_FW_NPTV6_CREATE`
- `IP_FW_NPTV6_DESTROY`
- `IP_FW_NPTV6_STATS`
- `IP_FW_NPTV6_RESET_STATS`
- `IP_FW_NPTV6_LIST`

## Output Behavior
`show` prints:
- optional set
- instance name
- internal prefix
- either external prefix or external interface
- prefix length

## Notable Edge Cases
- Rejects specifying both `ext_prefix` and `ext_if`.
- Rejects mismatched embedded prefix lengths and explicit `prefixlen`.
- Interface names must fit in `cfg->if_name`.
