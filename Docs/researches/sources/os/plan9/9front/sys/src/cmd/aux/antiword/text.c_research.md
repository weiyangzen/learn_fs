# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/text.c

Plain text output backend.

Key responsibilities:
- Initializes text output state from options and diagram coordinates.
- Emits final newline in the epilogue.
- Writes substrings to the output file and advances horizontal position.
- Converts non-breaking spaces to normal spaces for non-UTF-8 output.
- Emits leading filler spaces based on current X position when moving to a new line.
- Handles paragraph/page boundaries as newline operations.

Important behavior:
- UTF-8 output strings are written byte-for-byte.
- Large before/after paragraph gaps become blank lines.
- This backend keeps formatting intentionally coarse: indentation and line breaks only.

Dependencies:
- Diagram/output abstraction, option encoding, width conversion helpers.

Research relevance:
- Final plain-text rendering endpoint for the parser pipeline.
