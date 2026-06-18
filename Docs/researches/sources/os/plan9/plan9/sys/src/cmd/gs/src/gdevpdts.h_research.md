# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdts.h

## Purpose
Defines text-state values and APIs shared inside the `pdfwrite` text subsystem.

## Main Definitions
- Forward declares `pdf_text_state_t`.
- Defines `pdf_text_state_values_t`, the client-facing state that can be translated into PDF text operators:
  - Character spacing (`Tc`)
  - Font resource and size (`Tf`)
  - Text matrix (`Tm` and related positioning)
  - Render mode (`Tr`)
  - Word spacing (`Tw`)
- Defines `TEXT_STATE_VALUES_DEFAULT`.

## API Surface
- Context transitions:
  - `pdf_from_stream_to_text`
  - `pdf_from_string_to_text`
  - `pdf_close_text_contents`
- Internal text code helpers:
  - `pdf_render_mode_uses_stroke`
  - `pdf_get_text_state_values`
  - `pdf_set_text_wmode`
  - `pdf_set_text_state_values`
  - `pdf_text_distance_transform`
  - `pdf_text_position`
  - `pdf_append_chars`

## Integration
- Used by text processing modules to update PDF text state without knowing the buffering internals in `gdevpdts.c`.
- Includes `gsmatrix.h` because matrices are part of the public text-state value contract.

## Risks and Notes
- The matrix is documented as text-space to user/device-space after combining PostScript CTM, FontMatrix, and inverse font size scaling; callers must pass the correct coordinate-space matrix.
