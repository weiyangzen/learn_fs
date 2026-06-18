# File Research: sources/os/plan9/9front/sys/src/cmd/mk/graph.c

Builds and validates the dependency graph for a target.

Key behavior:
- `graph()` applies explicit and meta rules, detects cycles, prunes vacuous arcs, checks ambiguous recipes, and applies node attributes.
- `applyrules()` recursively creates/reuses `Node`s, expands normal `%/&` meta rules and regexp rules, and tracks rule recursion counts with `NREP`.
- `vacuous()` removes meta-rule arcs that lead only to non-probable targets.
- `ambiguous()` rejects multiple incompatible recipes, preferring explicit over meta recipes where possible.
- `attribute()` propagates rule attributes like virtual, no-recipe, and delete to nodes.

Important dependencies: `mk.h`, `match`, `subst`, Plan 9 regexp `regexec/regsub`, `symlook`, `newarc`, `timeof`.

Notable risks:
- Recursive rule expansion is limited by rule counters; bad `NREP` values can change graph completeness.
- Ambiguity checks compare recipe pointer identity, not text equality.
