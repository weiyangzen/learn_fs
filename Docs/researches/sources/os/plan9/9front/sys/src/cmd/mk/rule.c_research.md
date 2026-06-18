# File Research: sources/os/plan9/9front/sys/src/cmd/mk/rule.c

Stores parsed rules and maintains explicit/meta rule lists.

Key behavior:
- `addrule()` reuses a rule with the same target/tail when possible, otherwise allocates a new `Rule`.
- Adds explicit rules to `rules` and meta/regexp rules to `metarules`.
- Compiles regexp rule targets with `regcomp`.
- Maintains per-target chains through `S_TARGET`.
- `rulecnt()` allocates the per-rule recursion counter array.

Important dependencies: `mk.h`, `symlook`, `wcmp`, `regcomp`, global `patrule`.

Notable risks:
- Reused rules overwrite fields like recipe/body/line while retaining target chain identity.
- Rule numbering drives recursion-limit bookkeeping.
