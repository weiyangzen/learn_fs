# File Research: sources/os/plan9/9front/sys/src/cmd/mothra/libpanel/pldefs.h

Internal libpanel definitions and helper declarations.

Key behavior:
- Declares rich-text formatting/drawing/hit internals.
- Defines internal flags (`HITME`, `LEAF`, `INVIS`, `REMOUSE`) and widget state/style constants.
- Defines scroll command constants and scrollbar/slider orientation constants.
- Declares drawing primitives, panel allocation/printing/hit helpers, UTF helpers, and `Textwin` internals.

Important dependencies: `panel.h` and implementation files.

Notable risks:
- Internal flag ranges must not collide with public panel flags.
- `Textwin` location coordinates are absolute, causing special move handling.
