# File Research: sources/os/plan9/plan9/sys/src/cmd/spell/code.h

Affix-code bit definitions for Plan 9 spell.

Key contents:
- Defines bit masks for suffix/prefix classes such as `ED`, `ADJ`, `NOUN`, `ACTOR`, `ION`, `N_AFFIX`, `V_AFFIX`, `MAN`, `ADV`, `STOP`, `NOPREF`, `MONO`, `IN`, and `_Y`.
- Defines combined masks such as `COMP`, `VERB`, and `ALL`.

Important details:
- Used by both dictionary encoder `pcode.c` and runtime analyzer `sprog.c`.
- `ALL` excludes stop/no-prefix/do-not-touch/mono/in flags.

Filesystem relevance:
- None directly; spell dictionary metadata.
