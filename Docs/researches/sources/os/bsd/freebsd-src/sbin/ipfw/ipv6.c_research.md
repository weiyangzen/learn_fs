# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/ipv6.c

## Purpose

`ipv6.c` implements IPv6-specific parsing and formatting helpers for the `ipfw` rule compiler and printer. It handles IPv6 unreachable codes, IPv6 address operands, ICMPv6 type bitsets, IPv6 flow-id lists, and IPv6 extension-header masks.

The file is deliberately narrower than `ipfw2.c`: it exports helpers consumed by the main rule compiler/printer while keeping IPv6 address-specific logic out of the large core file.

## Public Surface

Exported functions:

- `uint16_t get_unreach6_code(const char *str)`
- `void print_unreach6_code(struct buf_pr *bp, uint16_t code)`
- `void print_ip6(struct buf_pr *bp, const ipfw_insn_ip6 *cmd)`
- `void fill_icmp6types(ipfw_insn_icmp6 *cmd, char *av, int cblen)`
- `void print_icmp6types(struct buf_pr *bp, const ipfw_insn_u32 *cmd)`
- `void print_flow6id(struct buf_pr *bp, const ipfw_insn_u32 *cmd)`
- `int fill_ext6hdr(ipfw_insn *cmd, char *av)`
- `void print_ext6hdr(struct buf_pr *bp, const ipfw_insn *cmd)`
- `ipfw_insn *add_srcip6(ipfw_insn *cmd, char *av, int cblen, struct tidx *tstate)`
- `ipfw_insn *add_dstip6(ipfw_insn *cmd, char *av, int cblen, struct tidx *tstate)`
- `void fill_flow6(ipfw_insn_u32 *cmd, char *av, int cblen)`

## Address Parsing

`fill_ip6()` is the central internal parser. It accepts:

- `any`, producing an empty/no-op instruction,
- `me` and `me6`,
- `table(...)`, delegated to `fill_table()` with `O_IP_DST_LOOKUP` before source/destination opcode adjustment,
- single IPv6 addresses,
- address plus prefix length,
- address plus explicit IPv6 mask,
- comma-separated address/mask lists.

It resolves numeric IPv6 addresses with `inet_pton()` and hostnames with `gethostbyname2(AF_INET6)`. It applies masks with `APPLY_MASK()`, stores single-address cases compactly, and stores lists as address/mask pairs.

`add_srcip6()` and `add_dstip6()` call `fill_ip6()` and then choose the final opcode:

- source/destination `me6`,
- single source/destination IPv6,
- source/destination IPv6 mask list,
- table lookup variants.

## Formatting

`print_ip6()` reconstructs CLI syntax from packed IPv6 instructions. It handles:

- `me6`,
- generic `ip6`,
- single addresses,
- address/mask pairs,
- `any`,
- optional reverse lookup via `g_co.do_resolv`,
- non-contiguous masks by printing explicit mask addresses.

`print_unreach6_code()`, `print_icmp6types()`, `print_flow6id()`, and `print_ext6hdr()` provide specialized printing for action and option operands.

## ICMPv6, Flow ID, and Extension Headers

`icmp6codes[]` maps textual unreachable names such as `no-route`, `admin-prohib`, `address`, and `port` to ICMPv6 destination-unreachable codes.

`fill_icmp6types()` parses comma-separated numeric type values into a bitmap instruction. It validates separators and rejects values above `ICMP6_MAXTYPE`.

`fill_flow6()` parses comma-separated 20-bit flow labels into a variable-length `ipfw_insn_u32` instruction and stores the count in `o.arg1`.

`ext6hdrcodes[]` maps extension-header tokens:

- `frag`
- `hopopt`
- `route`
- `dstopt`
- `ah`
- `esp`
- `rthdr0`
- `rthdr2`

`fill_ext6hdr()` ORs these into `cmd->arg1`, sets `O_EXT_HDR`, and returns whether any valid bit was set.

## Dependencies

This file depends on shared helpers from `ipfw2.c`:

- `match_token()` / `match_value()`
- `bprintf()`
- `contigmask()`
- `n2mask()`
- `fill_table()`
- global `g_co`

It also depends on kernel instruction layout macros and opcodes from `<netinet/ip_fw.h>`.

## Error Handling and Risks

Most malformed operands terminate with `errx(EX_DATAERR, ...)`.

Risk points:

- Like the IPv4 parser, `fill_ip6()` mutates the argument string by inserting NUL terminators around commas and slashes. Callers must provide mutable storage.
- `fill_ip6()` uses `strdup()` but exits via `errx()` on many parse failures before freeing; this is acceptable for a short-lived CLI process but relevant for reuse.
- `fill_flow6()` calls `strtoul(av, &av, 0)` after `strsep()` and then checks `*av != ','`; because `strsep()` already split at commas, only the end-of-token check matters in practice.
- The comment in `fill_icmp6types()` questions whether the upper bound should allow all 8-bit values rather than `ICMP6_MAXTYPE`.

## Testing Notes

Useful tests:

- Source and destination IPv6 `any`, `me6`, single address, prefix, explicit mask, and comma-list operands.
- Table-backed IPv6 operands.
- Non-contiguous mask printing.
- ICMPv6 unreachable code names and numeric values.
- ICMPv6 type lists at boundary values.
- Extension-header parse/print round trips.
- Flow labels at `0`, valid maximum `0xfffff`, and out-of-range values.
