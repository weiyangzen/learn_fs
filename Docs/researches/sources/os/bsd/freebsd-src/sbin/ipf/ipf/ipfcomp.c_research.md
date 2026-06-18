# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipf/ipfcomp.c

## Purpose
Generates C source/header output for compiled IPFilter rule sets.

## Main Elements
- `printc()` writes `ip_rules.c` rule data for eligible IPv4 normal IPF rules.
- Groups rules by group name and input/output direction.
- Emits serialized `frentry_t` data and optional rule data blocks.
- `printC()`, `printCgroup()`, and `emitGroup()` generate matcher functions with nested comparisons for interface, version, flags, protocol, TTL, TOS, TCP flags, ports, source/destination addresses, options, security, auth, and ICMP fields.
- Orders comparisons based on commonality across following rules using `mc_t` metrics.
- `printhooks()` emits add/remove helper functions that register compiled matchers with IPFilter via `frrequest()`.
- `emittail()` emits aggregate `ipfrule_add()` and `ipfrule_remove()` functions.

## Dependencies And Integration
Called from `ipf.c` when `-cc` output mode is selected. Produces `ip_rules.c` and `ip_rules.h` for kernel compiled-rule integration under `IPFILTER_COMPILED`.

## Risk Notes
Only a subset of rules is eligible: IPv6, non-IPF, BPF/expression, and lookup-address forms are skipped. Generated header text contains suspicious doubled closing parentheses in some prototypes, so this path needs careful build verification.
