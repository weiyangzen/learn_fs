# File Research: sources/os/plan9/9front/sys/src/cmd/spell/code.h

`code.h` defines the affix/class bitmask vocabulary shared by the spelling dictionary encoder (`pcode.c`) and spelling recognizer (`sprog.c`). The constants describe which derivational or inflectional transformations are valid for a base dictionary word.

The bits cover suffix classes such as `ED`, `ADJ`, `NOUN`, `ACTOR`, `ION`, `N_AFFIX`, `V_AFFIX`, `V_IRREG`, `MAN`, `ADV`, and `_Y`; special handling flags such as `DONT_TOUCH`, `STOP`, `NOPREF`, `MONO`, and `IN`; and convenience combinations such as `COMP`, `VERB`, and `ALL`.

This header is pure data contract. Changes here must stay synchronized with `pcode.c` string-to-bit encoding, `sprog.c` suffix/prefix logic, and any existing encoded dictionary files, because the binary dictionary stores these bit meanings by value.
