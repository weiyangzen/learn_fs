# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdts.c

Text state management for `pdfwrite`. It buffers text and inter-character moves, tracks client-side versus emitted PDF text state, emits text-state operators, and transitions between PDF stream/text/string contexts.

Key behavior:
- Defines an internal text buffer with up to 200 characters and 50 movement entries.
- Maintains two text-state value sets: `in`, reflecting current client/Ghostscript state, and `out`, reflecting the state already emitted to the PDF stream.
- Tracks buffer start position, WMode, leading, line continuation, line start, and output position.
- `append_text_move` adds TJ movement values, merges adjacent moves, rounds near-integers, and rejects movement values that exceed Acrobat limits.
- `set_text_distance` converts device/user deltas back into text-space deltas and rounds near-integers.
- `add_text_delta_move` tries to express a text matrix translation as a TJ offset when transformation parts are compatible and the move is in writing direction.
- `pdf_set_text_matrix` emits `TL`/`T*`, `Td`, or `Tm` depending on how the text matrix changes; `Tm` is adjusted by device resolution scaling.
- Allocates, defaults, copies, page-resets, and grestore-resets `pdf_text_state_t`.
- `pdf_from_stream_to_text` initializes state when entering text from regular stream context.
- `flush_text_buffer` emits either a simple string plus `Tj`/apostrophe or an array plus `TJ`, including embedded movement offsets.
- `sync_text_state` emits changed text state operators (`Tc`, `Tf`, `Tm`/`Td`/leading, `Tr`, `Tw`) before flushing buffered text.
- `pdf_from_string_to_text` flushes/synchronizes accumulated string context back to text context.
- `pdf_close_text_contents` clears current font pointers and sizes.
- `pdf_render_mode_uses_stroke` detects render-mode changes that require stroke-state preparation.
- `pdf_get_text_state_values`, `pdf_set_text_wmode`, and `pdf_set_text_state_values` expose and update the client-side text state.
- `pdf_set_text_state_values` attempts to fold position-only changes into TJ offsets before flushing; otherwise it synchronizes the current buffer.
- `pdf_text_distance_transform` and `pdf_text_position` expose current text-space coordinate behavior.
- `pdf_append_chars` opens the page in string context, appends bytes into the buffer, flushes when full, preserves continuation state, and advances input/output positions.

Notable dependencies:
- Uses `gdevpdfx.h` for page/context operations and `gdevpdtf.h` for font resource details.
- Uses Ghostscript matrix/math helpers and PDF string/name emission helpers.

Research notes:
- This file is a state-delta engine for efficient PDF text output, choosing compact `Tj`, `TJ`, `Td`, `Tm`, `TL`, and related operators.
- The buffering logic is constrained by old Acrobat movement and coordinate limits.
- It intentionally emits `Tw` only when the buffered text contains space characters.
- This is text stream output infrastructure, not filesystem functionality.
