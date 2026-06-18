# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont0.c

## Role

`gsfont0.c` implements generic Type 0 composite font GC support and matrix-adjustment hooks for defining and scaling composite fonts.

This is composite font infrastructure, not filesystem code.

## Main Interfaces

- `gs_type0_define_font`
- `gs_type0_make_font`

## Core Behavior

The GC descriptor enumerates and relocates:

- `data.Encoding`
- `data.FDepVector`
- either `data.SubsVector` or `data.CMap`, depending on `FMapType`

When a composite font has a non-identity `FontMatrix`, `gs_type0_adjust_matrix` copies `FDepVector` and applies `gs_makefont` to descendant composite fonts so descendant matrices incorporate the parent transform.

## Important Details

- Identity matrices avoid descendant adjustment.
- Only descendant fonts with `FontType == ft_composite` are adjusted.
- A new `FDepVector` is allocated before modifying descendants.

## Notable Risks

- If a descendant adjustment fails after allocating a copied dependency vector, the function returns the error without visible cleanup of the partially allocated vector.
