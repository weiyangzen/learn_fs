# File Research: sources/os/plan9/9front/sys/src/cmd/abaco/fonts.h

Default Abaco font path table included into `util.c`.

Key contents:
- Lists Lucida Sans regular, italic, and bold Unicode fonts at five sizes.
- Lists fixed-width Unicode fonts at five sizes.
- Provides exactly the default entries expected by `NumFnt`.

Role:
- Supplies fallback font paths when `$home/lib/abaco.fonts` is absent or incomplete.

Notable risks:
- This is not a standalone C header with declarations; it is an initializer fragment.
