# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/memdraw.h

Drawterm copy of Plan 9 libmemdraw’s in-memory image API.

Key contents:
- Defines `Memdata`, `Memimage`, `Memcmap`, `Memsubfont`, draw flags, and `Memdrawparam`.
- Declares memory image allocation, load/unload, address calculation, clipping, fill, channel setup, pixel conversion, drawing primitives, string/subfont functions, colormap initialization, and predefined memory images.
- Includes an `X` pointer in `Memimage` used by the X11 backend for platform-specific pixmap state.

Role in this group:
- Core in-memory drawing substrate used by all GUI backends and drawterm screen rendering.

Notable risks:
- The `X` backend hook is a portability escape hatch and requires platform wrappers to keep memory and device state coherent.
- `Memdata` comments reference compaction/back-pointer behavior from Plan 9 that may not fully apply in drawterm.
