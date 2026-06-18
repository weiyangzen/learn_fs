# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/include/draw.h

Drawterm copy of Plan 9 libdraw’s public drawing API and data model.

Key contents:
- Defines drawing colors, refresh modes, line endings, Porter-Duff draw operations, image channel descriptors, common channel constants, `Point`, `Rectangle`, `Display`, `Image`, `Screen`, fonts, subfonts, glyph cache records, and RGB values.
- Declares image allocation/loading, display management, window/screen APIs, geometry helpers, colormap helpers, drawing primitives, string/font functions, subfont management, and compressed image helpers.
- Declares global draw state such as `display`, `font`, `_screen`, and debug flags.

Role in this group:
- Provides the central graphics contract consumed by GUI backends and drawterm terminal/display code.

Notable risks:
- This header intentionally mirrors Plan 9 APIs and relies on many implementations elsewhere.
- Several globals and compatibility macros make namespace collisions likely without the surrounding `u.h` remapping.
