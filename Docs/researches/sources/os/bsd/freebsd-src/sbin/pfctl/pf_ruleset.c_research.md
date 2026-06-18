# File Research: sources/os/bsd/freebsd-src/sbin/pfctl/pf_ruleset.c

## Purpose
Manages pfctl's in-memory normal and Ethernet anchor/ruleset hierarchy while parsing and assembling rules. It creates, finds, links, initializes, and removes rulesets and attaches anchor references to rules.

## Main Elements
- Defines global parser-side anchor state and RB-tree operations for normal anchors.
- `pf_get_ruleset_number()` maps PF actions to scrub, filter, NAT, binat, or rdr ruleset indexes.
- `pf_find_ruleset()` and `pf_find_or_create_ruleset()` find or build normal anchor paths.
- `pf_remove_if_empty_ruleset()` removes unreferenced normal anchors with no child anchors, tables, open table operations, or queued rules.
- Ethernet support includes `pf_init_eth_ruleset()`, recursive anchor lookup, `pf_find_or_create_eth_ruleset()`, and `pfctl_eth_anchor_setup()`.
- `pfctl_anchor_setup()` resolves absolute/relative normal anchor names, handles `../` traversal and `/*` wildcards, creates target rulesets, and increments reference counts.

## Dependencies And Integration
Uses PF and pfctl parser structures from `pfctl.h`, `pfctl_parser.h`, `<net/pfvar.h>`, and FreeBSD queue/tree macros. Called heavily by `parse.y` for anchor rules and inline anchor blocks.

## Risk Notes
Anchor tree integrity depends on synchronized RB-tree insertion/removal. `pf_remove_if_empty_eth_ruleset()` currently returns immediately, so Ethernet empty-anchor cleanup logic below it is unreachable.
