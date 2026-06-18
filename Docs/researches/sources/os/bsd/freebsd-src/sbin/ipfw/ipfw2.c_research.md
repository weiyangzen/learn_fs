# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/ipfw2.c

## Purpose

`ipfw2.c` is the main implementation of the FreeBSD `ipfw` userland rule engine. It owns global command options, shared utility routines, socket communication with the kernel, token tables, rule display, dynamic-state display, set operations, sysctl toggles, rule deletion/zeroing/flushing, object lookup/packing, and the large rule compiler used by `ipfw add`.

It is the behavioral center of this file group. `main.c` dispatches here; `ipv6.c` and `dummynet.c` provide helper surfaces used from here or routed through `g_co`; `ipfw2.h` exports the shared contract.

## Public Surface

Externally visible functions implemented here include:

- `int is_ipfw(void)`
- buffer helpers: `bp_alloc()`, `bp_free()`, `bp_flush()`, `bprintf()`, `pr_u64()`
- allocation helpers: `safe_calloc()`, `safe_realloc()`
- parser helpers: `_substrcmp()`, `_substrcmp2()`, `stringnum_cmp()`, `match_token()`, `match_token_relaxed()`, `get_token()`, `match_value()`, `concat_tokens()`, `fill_flags()`, `print_flags_buffer()`
- kernel operation wrappers: `do_cmd()`, `do_set3()`, `do_get3()`
- rule/control handlers: `ipfw_add()`, `ipfw_delete()`, `ipfw_flush()`, `ipfw_zero()`, `ipfw_list()`, `ipfw_sets_handler()`, `ipfw_sysctl_handler()`, `ipfw_internal_handler()`
- shared rule helpers: `n2mask()`, `fill_table()`, `ipfw_check_object_name()`

## Global State and Tables

The file defines:

- `struct cmdline_opts g_co`: global command options set by `main.c`.
- `int resvd_set_number = RESVD_SET`: exported reserved set upper bound.
- `static int ipfw_socket = -1`: lazily opened raw IPv4 socket for kernel control calls.
- `struct format_opts`: per-listing display configuration, including counter widths, set masks, requested rule range, dynamic-state count, and table/object name state.

Static token tables encode the command grammar: TCP flags/options, IP options/TOS/offset flags, DSCP names, limit masks, EtherTypes, rule actions, external actions, action parameters, lookup keys, table-value names, and rule options.

## Kernel Operation Model

The file uses a raw socket to issue classic and versioned ipfw operations:

- `do_cmd()` supports legacy `setsockopt()` plus `getsockopt()` when the option name is negative or `IP_FW3`.
- `do_set3()` writes an `ip_fw3_opheader` and calls `setsockopt(IP_FW3)`.
- `do_get3()` writes an `ip_fw3_opheader` and calls `getsockopt(IP_FW3)`.

Global flags affect this layer:

- `g_co.debug_only` dumps binary request headers and payloads to stdout.
- `g_co.test_only` short-circuits kernel calls and returns success.

Most higher-level operations build packed TLV/control buffers, then call `do_get3()` or `do_range_cmd()`.

## Rule Display

Rule display is organized around `show_static_rule()` and `show_state`.

`show_static_rule()`:

1. Skips disabled sets unless `show_sets` is requested.
2. Prints rule number, optional counters, timestamp, and set number.
3. Prints probability, action, action modifiers, protocol, source, destination, and remaining options.
4. Handles compact/comment-only modes.
5. Prints comments stored as `O_NOP`.

The printer uses `show_state.printed[]` to avoid printing the same instruction twice while reconstructing canonical CLI syntax from packed kernel instructions. It has dedicated formatters for IPv4/IPv6 addresses, table lookups, MAC addresses, ports/ranges, DSCP, ICMP types, TCP/IP flags, forwarding addresses, state names, external actions, marks, tags, and dynamic states.

Dynamic states are formatted by `show_dyn_state()` and reached through `foreach_state()`/`list_dyn_range()`. It supports IPv4 and IPv6 flow identifiers, state names, parent/limit/keep-state types, counters, expirations, and verbose TCP state flags.

## Listing Configuration

`ipfw_list()` parses optional rule/range filters, decides whether static rules, dynamic states, and counters are needed, retrieves configuration with `ipfw_get_config()`, and calls `ipfw_show_config()`.

`ipfw_get_config()` retries up to 16 times with larger buffers on `ENOMEM`. Returned configuration can include:

- table/object name TLVs,
- static rule list TLVs,
- dynamic state TLVs.

`ipfw_show_config()` sorts object names, initializes formatting widths, lists all rules or specific requested ranges, and returns `EX_UNAVAILABLE` when requested static rules are missing.

When `g_co.do_pipe` is set, `ipfw_list()` delegates directly to `dummynet_list()`.

## Set, Sysctl, Delete, Zero, and Flush Operations

`ipfw_sets_handler()` supports:

- `set show`
- `set swap X Y`
- `set move X to Y`
- `set move rule X to Y`
- mixed `set enable`/`disable` masks

It uses `do_range_cmd()` and `IP_FW_SET_*`/`IP_FW_XMOVE` operations.

`ipfw_sysctl_handler()` toggles firewall, one-pass, debug, verbose, dynamic keepalive, skipto cache, and optionally ALTQ. Skipto cache is handled through a versioned `IP_FW_SKIPTO_CACHE` request rather than a sysctl.

`ipfw_delete()` deletes rules, sets, NAT configs, or dummynet objects depending on `g_co`. It supports rule ranges and dynamic-only deletion through `g_co.do_dynamic == 2`.

`ipfw_zero()` zeroes counters or log counters for all rules or selected rules.

`ipfw_flush()` prompts unless forced/quiet, delegates to `dummynet_flush()` for pipes, and otherwise deletes all rules or a selected set.

## Object Name Packing

The compiler uses `struct tidx` to collect referenced named kernel objects before submitting a rule:

- tables,
- state names,
- external actions,
- external action instances.

`pack_object()` de-duplicates by name, set, and TLV type, assigns local indices, and grows the object array. `pack_table()` wraps table-name validation. `object_sort_ctlv()`, `object_search_ctlv()`, and `table_search_ctlv()` sort and search kernel/user object TLVs.

`fill_table()` parses `table(NAME)` and `table(NAME,value)` or `table(NAME,key=value)`, sets lookup/table-value flags, and embeds the packed table index in an instruction.

## Rule Compiler

`compile_rule()` parses `ipfw add` syntax and assembles the packed `struct ip_fw_rule` instruction stream. It is the most complex function in the file.

It uses separate temporary buffers:

- `cmdbuf[]` for match instructions.
- `actbuf[]` for actions.
- caller-provided `rbuf` for the final rule.

The compiler handles:

- optional rule number,
- optional `set N`,
- optional `prob D`,
- mandatory action,
- action parameters such as `log`, `altq`, `tag`, and `untag`,
- `proto from src [ports] to dst [ports]`,
- option-only rule forms,
- `not` and OR blocks with braces/parentheses,
- comments.

Supported actions include allow/deny/count, reject/reset/unreach for IPv4 and IPv6, skipto, pipe/queue, divert/tee, netgraph/ngtee, fwd IPv4/IPv6, NAT, reass, setfib, setdscp, call/return, setmark, external actions, and `tcp-setmss`.

Supported match options include IPv4/IPv6 source/destination, table lookups with optional masks, MAC table lookups, MAC address/type matches, ports/ranges/service names, uid/gid/jail, TCP flags/options/sequence/ack/window/MSS/data length, IP length/id/TTL/version/precedence/TOS/options/DSCP, ICMP/ICMPv6 types, IPv6 extension headers and flow IDs, in/out/via/xmit/recv, fib, sockarg, tagged, mark, stateful `keep-state`/`record-state`, `limit`/`set-limit`, reverse-path checks, antispoof, ipsec, and defer-action.

Final instruction ordering is deliberate:

1. Match probability.
2. Generated `O_PROBE_STATE` for stateful rules when needed.
3. Match instructions excluding late-position state/action modifiers.
4. `O_KEEP_STATE` or `O_LIMIT`.
5. `O_SKIP_ACTION`.
6. Action-section offset.
7. `O_LOG`, `O_ALTQ`, `O_TAG`.
8. Actual actions.

`ipfw_add()` wraps the compiled rule in `IPFW_TLV_RULE_LIST`, optionally prepends `IPFW_TLV_TBLNAME_LIST`, aligns rule size to 64-bit boundaries, sends `IP_FW_XADD`, and prints the resulting rule unless quiet.

## Address and Operand Parsing

IPv4 handling is local to this file:

- `fill_ip()` supports `me`, `any`, single addresses, masks by `/bits` or `:mask`, address lists, and `/24`-to-`/31` compact address sets.
- `add_srcip()` and `add_dstip()` map the filled instruction to source/destination opcodes.
- `lookup_host()` resolves IPv4 hostnames.

IPv6 handling is delegated to `ipv6.c` through `add_srcip6()`, `add_dstip6()`, `fill_icmp6types()`, `fill_flow6()`, and `fill_ext6hdr()`.

Port parsing uses `strtoport()` with service-name lookup, EtherType-name lookup for MAC type, range support, and comma-separated lists.

## Internal Commands and Monitoring

`ipfw_internal_handler()` dispatches hidden/internal commands:

- `iflist`: tracked interface list via `IP_FW_XIFLIST`.
- `talist`: table algo list from `tables.c`.
- `olist`: service object list via `IP_FW_DUMP_SRVOBJECTS`.
- `vlist`: table value list from `tables.c`.
- `monitor`: route-socket firewall log monitor.

`ipfw_rtsock_monitor()` opens `socket(PF_ROUTE, SOCK_RAW, AF_IPFWLOG)` and continuously decodes `RTM_IPFWLOG` messages with Ethernet addresses, source/destination socket addresses, set/rule/tablearg/opcode/mark metadata, optional next-hop, and optional comment filtering.

## Error Handling and Risks

The code uses `err()`/`errx()` heavily and generally exits on malformed input. It performs many command-buffer length checks through `CHECK_LENGTH`, `CHECK_CMDLEN`, `CHECK_ACTLEN`, and `CHECK_RBUFLEN`.

Important risk areas:

- `compile_rule()` mutates argument strings in place using `strsep()`, inserted NULs, and pointer increments; callers must pass mutable argument storage.
- `compile_rule()` uses fixed temporary instruction arrays of 255 `uint32_t`; length checks reduce risk but every new opcode path must update length before writing payload fields.
- `do_set3()` debug initializer contains `.total_len = optlen, sizeof(struct debug_header),` which uses the comma operator in an initializer-like expression and appears intended to include the debug header size. This should be reviewed if debug binary output matters.
- `concat_tokens()` increments `bufsize` instead of decreasing remaining capacity after `snprintf()`; this utility appears suspicious and should be tested before reuse for bounded output.
- `eaction_check_name()` rejects a name only when it is present in both `rule_actions` and `rule_action_params`; the comment says it restricts special names, but the condition may not match the intended union-style restriction.
- Some action paths increment `av` after accepting keywords where a missing argument would already have failed, but changes to optional argument syntax can easily desynchronize parsing.
- Object TLV search assumes sorted kernel-provided object lists with fixed object size; callers must sort user-built lists before kernel submission.

## Testing Notes

High-value tests would cover:

- `ipfw add` dry-run/debug output for representative actions and every address family.
- Canonical print round-trips for rules with tables, named states, comments, OR blocks, `not`, and external actions.
- Dynamic state list decoding.
- Buffer-boundary tests for long comments, large port lists, many table references, and long rule option chains.
- `set`, `delete`, `zero`, and `flush` range/set behavior.
- `lookup key:mask table` variations for supported and unsupported key types.
