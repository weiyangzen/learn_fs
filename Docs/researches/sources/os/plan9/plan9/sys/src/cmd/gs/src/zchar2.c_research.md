# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar2.c

Provides the Type 2 character display operator.

Key behavior:
- `.type2execchar` calls the shared `charstring_execchar` implementation from `zchar1.c`, restricted to `ft_encrypted2`.
- The file intentionally contains only the thin Type 2 dispatch layer.

Dependencies and coupling:
- Requires `ichar1.h` for `charstring_execchar`.
- All substantive Type 2 CharString execution behavior is inherited from `zchar1.c`.
