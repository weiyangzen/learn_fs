# File Research: sources/os/bsd/freebsd-src/sbin/ipfw/ipfw2.h

## Purpose

`ipfw2.h` is the shared declaration and token header for the `ipfw`/`dnctl` userland sources. It defines global command-line state, parser token ids, common macros, the dynamic print buffer type, utility prototypes, kernel operation wrappers, and cross-file command handler declarations.

It intentionally forward-declares many kernel ABI structs instead of including every heavy network header in each source file.

## Key Definitions

`enum cmdline_prog` distinguishes whether the binary is acting as:

- `cmdline_prog_ipfw`
- `cmdline_prog_dnctl`

`struct cmdline_opts` is global CLI state. Major flags include:

- display modes: counters, compact, comments-only, timestamps, set display, sorting, resolving names,
- behavior modes: quiet, force, test-only, debug-only,
- command target modes: pipe/queue/scheduler, NAT, dynamic state handling, selected set,
- `prog` to distinguish `ipfw` from `dnctl`.

The comment notes that when reading commands from a file, option context is not restored after each line. That is an important behavior inherited by `main.c`.

`struct _s_x` is the string-to-token table type used across parsers. `f_ipdscp[]` is exported for DSCP name lookup.

## Token Namespace

`enum tokens` is a large shared token namespace for:

- parser punctuation: `TOK_OR`, `TOK_NOT`, braces,
- rule actions: accept/count/pipe/queue/divert/forward/deny/reject/reset/check-state/NAT/reass/call/return/external actions,
- action parameters: log, ALTQ, tag/untag,
- rule options: UID/GID/jail, in/out/via/xmit/recv, layer2, diverted variants, IP/TCP/ICMP fields, MAC fields, stateful options, comments,
- dummynet options: PLR, buckets, bandwidth, delay, queue, scheduler, RED/GRED/AQM, masks, profile, burst, weights/priorities,
- NAT and table options,
- IPv6 options and NAT64/NPTv6 options,
- newer mark/setmark and defer-action options.

Because the token enum is shared by multiple files, adding grammar in one source can require coordinated updates to this header and token tables in `ipfw2.c` or `dummynet.c`.

## Shared APIs

The header declares:

- buffer printing: `struct buf_pr`, `bp_alloc()`, `bp_free()`, `bp_flush()`, `bprintf()`, `pr_u64()`
- allocation wrappers: `safe_calloc()`, `safe_realloc()`
- token/string helpers: `_substrcmp()`, `_substrcmp2()`, `stringnum_cmp()`, `match_token()`, `match_token_relaxed()`, `get_token()`, `match_value()`, `concat_tokens()`
- flag helpers: `fill_flags()`, `print_flags_buffer()`
- kernel command wrappers: `do_cmd()`, `do_set3()`, `do_get3()`
- mask helpers: `n2mask()`, `contigmask()`

It also declares first-level handlers implemented across the `sbin/ipfw` directory: add/list/delete/flush/zero, dummynet, NAT, tables, sysctl toggles, internal commands, NAT64/NPTv6, and validation helpers.

## Cross-File Boundaries

The header makes the following boundaries explicit:

- `dummynet.c` exports dummynet list/config/delete/flush routines.
- `ipv6.c` exports IPv6 print and fill helpers.
- `ipfw2.c` exports table filling and general rule/config functions.
- `tables.c`, NAT, NAT64, NPTv6, and optional ALTQ modules provide other handlers not in this group.

The `PF` conditional controls ALTQ availability. Without `PF`, `NO_ALTQ` is defined and ALTQ-specific calls are compiled out in `ipfw2.c`.

## Error/Compatibility Macros

`NEED()` and `NEED1()` are parser convenience macros that terminate with `EX_USAGE` when required arguments are missing.

The header preserves historical parser compatibility through `_substrcmp()` and `_substrcmp2()` prototypes, which intentionally allow abbreviations but warn about deprecated substring matching.

## Risks and Extension Notes

The shared `enum tokens` can become fragile because many token values are used in independent static token tables. New tokens should be added carefully and tested in both parse and print paths.

`struct cmdline_opts` is process-global mutable state. File-based command execution reuses it line to line, and the header explicitly documents that context is not restored. New options should account for this persistence.

Forward declarations reduce include coupling but mean ABI mismatches are caught only when implementation files include the real kernel headers.
