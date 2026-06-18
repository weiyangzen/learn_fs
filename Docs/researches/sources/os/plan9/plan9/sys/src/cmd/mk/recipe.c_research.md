# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/recipe.c

Selects and prepares recipes for execution.

Key functions:
- `dorecipe(Node *node)` chooses the applicable rule recipe, handles no-recipe cases, builds target lists, gathers prerequisite and new-prerequisite lists, marks nodes `BEINGMADE`, and queues a `Job`.
- `addw()` appends unique word entries.

Behavior notes:
- For multi-target rules, builds a linked node list of targets needing the recipe.
- Regex rules use the current node as target/alltarget.
- Virtual or no-recipe nodes are updated without command execution.
- `-t` touches non-virtual targets instead of running recipes.
