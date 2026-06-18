# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdts.c

## Purpose
Implements PDF text-state management and buffered text emission. It tracks client-visible text state versus emitted PDF text state and writes compact PDF text operators only when needed.

## Main Structures
- `pdf_text_buffer_t` accumulates up to 200 characters and 50 movement adjustments.
- `pdf_text_state_t` stores:
  - Input/client state (`in`), current start point, buffer, and writing mode.
  - Output/PDF stream state (`out`), leading, line-continuation flags, line start, and output position.

## Main Functions
- Allocation/reset/copy:
  - `pdf_text_state_alloc`
  - `pdf_set_text_state_default`
  - `pdf_text_state_copy`
  - `pdf_reset_text_page`
  - `pdf_reset_text_state`
- Context transitions:
  - `pdf_from_stream_to_text`
  - `pdf_from_string_to_text`
  - `pdf_close_text_contents`
- Buffer/state synchronization:
  - `append_text_move`
  - `add_text_delta_move`
  - `pdf_set_text_matrix`
  - `flush_text_buffer`
  - `sync_text_state`
- Public state APIs:
  - `pdf_render_mode_uses_stroke`
  - `pdf_get_text_state_values`
  - `pdf_set_text_wmode`
  - `pdf_set_text_state_values`
  - `pdf_text_distance_transform`
  - `pdf_text_position`
  - `pdf_append_chars`

## Output Behavior
- Emits `Tc`, `Tf`, `Tm`, `Td`, `TL`, `T*`, `Tr`, `Tw`, `Tj`, and `TJ` as needed.
- Uses `TJ` movement entries to represent small compatible text-position deltas without flushing/repositioning.
- Uses leading optimization for line advances.
- Opens pages in `PDF_IN_STRING` when appending characters.

## Integration
- Called by simple/composite text processing (`gdevpdte.c`, `gdevpdtc.c`) and bitmap-image text emission (`gdevpdti.c`).
- Uses font-resource fields to derive writing mode and register Type 3 charproc resources.
- Relies on `gdevpdfx.h` stream/page context APIs.

## Risks and Notes
- Buffer limits are arbitrary; overflow forces synchronization and continuation handling.
- Acrobat coordinate limits influence movement thresholds.
- State comparison uses raw matrix memory comparison in places, so exact floating-point equality affects optimization choices.
