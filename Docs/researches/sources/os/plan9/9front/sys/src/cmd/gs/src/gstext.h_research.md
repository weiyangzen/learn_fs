# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gstext.h

Declares the public/device text interface and text operation encoding.

Key definitions:
- Operation flags describe the input source, width modification mode, requested output action, client intervention, and width return.
- Validation macros reject missing or multiple input/output modes, invalid single-item sizes, and simultaneous add/replace width modes.
- `gs_text_params_t` carries input bytes/chars/glyphs/single char/single glyph, optional deltas, space char/glyph, replacement width arrays, and width count.
- `dev_proc_text_begin` defines the device-side text begin procedure.
- Return codes from `gs_text_process` request rendering, client intervention, or CDevProc execution.
- `gs_text_cache_control_t` selects char width, cache device, or cache device 2 metrics.

Public API:
- Generic text begin/update/restart/resync/process/release functions.
- PostScript-equivalent begin helpers.
- Current font/char/glyph/width accessors and cache setup helpers.

Research notes:
- The interface is explicitly state-machine based: clients call begin, repeatedly process until completion/error, and respond to positive return codes.
