# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/env.c

Builds the environment passed to recipe commands.

Key data:
- `myenv[]` lists internal mk variables such as `target`, `stem`, `prereq`, `pid`, `nproc`, `newprereq`, `alltarget`, `newmember`, and `stem0` through `stem9`.
- Global `Envy *envy` stores name-to-word-list values.

Key functions:
- `initenv()` registers internal variables and imports OS environment via `readenv()`.
- `execinit()` rebuilds `envy` from internal variables plus exported mk variables.
- `buildenv(Job *j, int slot)` updates job-specific variables for a running recipe.
- `envinsert()`, `envupd()`, and `ecopy()` manage entries.

Behavior notes:
- `newmember` extracts archive member names from new prerequisites.
- Regex rules populate `stem0` through `stem9` from match captures.
- Variables marked `S_NOEXPORT` or internal variables are skipped during generic export copying.
