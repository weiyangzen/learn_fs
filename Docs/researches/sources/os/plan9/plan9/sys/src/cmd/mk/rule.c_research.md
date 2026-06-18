# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/rule.c

Stores and manages parsed build rules.

Key functions:
- `addrule()` creates or reuses a `Rule`, inserts it into target hash chain, and appends it to `rules` or `metarules`.
- Detects meta rules via regexp attribute or `%`/`&` in target.
- Compiles regexp rules with `regcomp`.
- `dumpr()` prints rule lists.
- `rcmp()` compares target and tail for rule reuse.
- `rulecnt()` allocates per-rule recursion counters.

Behavior notes:
- Each rule gets increasing `rule` index.
- Reused rules update fields but are not re-appended.
- Rule chains support multiple rules per explicit target.
