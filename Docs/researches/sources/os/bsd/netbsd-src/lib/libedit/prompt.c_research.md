# File Research: sources/os/bsd/netbsd-src/lib/libedit/prompt.c

## Purpose
Manages left and right prompt callbacks, prompt rendering, and prompt position accounting.

## Main Interfaces
- `prompt_init`: installs default prompt callbacks and clears positions.
- `prompt_end`: no-op teardown hook.
- `prompt_set`: installs prompt or right-prompt callback, ignore marker, and wide-mode flag.
- `prompt_get`: returns the active prompt callback and ignore marker.
- `prompt_print`: renders the selected prompt and updates display coordinates.

## Behavior
Default prompt callbacks return empty prompts. Custom prompt callbacks can be normal or escape-aware. `prompt_print` walks the returned prompt text and sends it through refresh output, tracking horizontal/vertical prompt position. The ignore marker allows non-printing prompt spans such as terminal color escapes to be excluded from column accounting.

## Dependencies
Uses refresh output helpers, `EditLine` prompt state, and prompt callback types from libedit headers.

## Risks And Notes
Incorrect prompt width accounting causes cursor-placement and right-prompt overlap bugs. Escape-aware prompts must correctly bracket ignored terminal-control bytes.
