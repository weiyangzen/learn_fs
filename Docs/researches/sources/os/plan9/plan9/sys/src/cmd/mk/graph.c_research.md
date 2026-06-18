# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/graph.c

Builds and validates the dependency graph for a target.

Key functions:
- `graph(target)` applies rules, checks cycles, prunes vacuous branches, rejects ambiguity, and applies attributes.
- `applyrules()` recursively matches explicit and meta rules, expands stems/regex substitutions, and creates arcs.
- `vacuous()` removes meta-rule paths that do not lead to probable targets.
- `cyclechk()` detects dependency cycles.
- `ambiguous()` rejects multiple conflicting recipes.
- `attribute()` propagates rule attributes into node flags.
- `newnode()` creates and caches a node with initial file time.
- `dumpn()` supports graph debugging.

Behavior notes:
- Rule recursion is bounded by per-rule counters from `rulecnt()` and `NREP`.
- Meta rules support both `%`/`&` patterns and regexp rules.
- Virtual nodes force time to `0`.
