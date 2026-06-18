# File Research: sources/os/plan9/9front/sys/src/cmd/mk/recipe.c

Selects and schedules the recipe for an out-of-date node.

Key behavior:
- Chooses the applicable recipe arc from a node’s prerequisites.
- Handles no-recipe virtual/no-recipe targets and optional touch mode.
- Builds job target lists for all targets of a rule, expanding meta-rule stems.
- Collects all prerequisites and newly out-of-date prerequisites.
- Marks targets `BEINGMADE` and queues a `Job` with `run()`.

Important dependencies: `mk.h`, `outofdate`, `symlook`, `subst`, `wadd`, `newjob`, `run`.

Notable risks:
- Multi-target rule behavior depends on node lookup and readiness of all related targets.
- A missing recipe for a non-virtual/non-NORECIPE target is fatal.
