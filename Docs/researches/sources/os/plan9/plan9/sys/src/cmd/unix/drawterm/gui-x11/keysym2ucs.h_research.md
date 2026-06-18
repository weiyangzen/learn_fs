# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/gui-x11/keysym2ucs.h

Small declaration header for X11 keysym-to-UCS conversion.

Key contents:
- Includes `<X11/X.h>` for `KeySym`.
- Declares `long keysym2ucs(KeySym keysym)`.

Role in this group:
- Shared between `x11.c` and the generated conversion implementation.

Notable risks:
- No include guard; repeated inclusion is only safe because contents are simple declarations.
