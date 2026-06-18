# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/bayes/regen.c

- Role: Generates the serialized DFA regex file used by `msgtok`.
- Behavior: Defines ignore patterns, keyword pattern, and `^From ` detector; compiles each into deterministic programs and writes three `# dreprog` blocks.
- Helpers: `strcpycase` expands lowercase letters outside character classes into case-insensitive classes; `dregcomp` wraps `regcomp` plus `dregcvt`.
- Risks/notes: Static 16 KiB regex assembly buffer assumes combined patterns fit.
