# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxchrout.h

Shared header for outline character rendering helpers.

Key declarations:
- Forward-declares `gs_imager_state`.
- Declares `double gs_char_flatness(const gs_imager_state *pis, floatp default_scale);`.

Behavior contract:
- The helper returns a character-specific flatness that may be lower than the imager state's flatness.
- `default_scale` is expected to be 0.001 for Type 1 fonts and 1.0 for TrueType fonts.

Research notes:
- The header intentionally exposes only the flatness computation, keeping outline rasterization details elsewhere.
