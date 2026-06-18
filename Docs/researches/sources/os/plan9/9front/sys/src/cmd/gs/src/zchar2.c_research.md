# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar2.c

This is a small Type 2 character display operator wrapper.

Key behavior:
- Defines `.type2execchar`.
- Delegates implementation to `charstring_execchar` with a font-type mask restricted to `ft_encrypted2`.

Important dependencies:
- Uses shared Type 1/Type 2 charstring execution declared in `ichar1.h`.
- Registered through `zchar2_op_defs`.

Research notes:
- Most Type 2 behavior lives in `zchar1.c`; this file only supplies the Type 2 operator entry point.
