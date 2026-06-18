# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfont0c.c

## Role

`gsfont0c.c` creates Type 0 wrapper fonts around CIDFont and Type 42 fonts, optionally using a TrueType cmap-derived CMap.

This is font wrapping/conversion support, not filesystem code.

## Main Interfaces

- `gs_font_type0_from_cidfont`
- `gs_font_type0_from_type42`

## Core Behavior

`type0_from_cidfont_cmap` allocates a Type 0 font, one-entry Encoding array, and one-entry FDepVector. It sets:

- `FontType = ft_composite`
- CMap-based mapping
- `FDepVector[0]` to the wrapped descendant font
- key/font names inherited from the wrapped font
- Type 0 init and next-character procedures

`gs_font_type0_from_cidfont` creates an identity CMap for the CIDFont. `gs_font_type0_from_type42` first converts Type 42 to CIDFontType 2, then wraps it with either a TrueType cmap-derived CMap or an identity CMap.

## Notable Risks

- Error paths contain explicit comments noting missing substructure cleanup.
- `font0->procs.make_font` is set to `0` because the wrapper path says it is not called; misuse outside that assumption would be unsafe.
