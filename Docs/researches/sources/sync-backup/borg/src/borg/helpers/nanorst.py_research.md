# sources/sync-backup/borg/src/borg/helpers/nanorst.py

## Purpose
Converts the limited reStructuredText used in Borg help text into plain or terminal-styled text without pulling in a full rST renderer.

## Important APIs, Types, And Functions
`TextPecker` is a small reader with `read`, `peek`, `peekline`, and `readline`. `process_directive` handles directives. `rst_to_text` performs conversion. `RstToTextLazy` delays conversion and proxies string behavior. `ansi_escapes` emits terminal escape transitions. `rst_to_terminal` chooses ANSI output based on `is_terminal`.

## Control Flow
`rst_to_text` scans character-by-character with states for plain text, inline emphasis/code markers, strong markers, literal code blocks, directives, and references. It supports custom `nanorst` inline fill/replace directives, directive rendering, reference substitution through a caller-provided map, escaped inline markers, and code-block exit on blank-line indentation rules.

## State And Persistence
All conversion state is local to the scanner. `RstToTextLazy` caches the converted string after first access. No persistent state.

## Dependencies And Integration Points
Used by CLI help formatting and terminal output. It depends on `helpers.is_terminal` imported through the package façade and standard streams.

## Risks And Edge Cases
This is intentionally loose parsing, not full rST. Unmatched inline states assert at the end. Missing references raise `ValueError` with a maintenance instruction. The parser relies on indexing semantics in `TextPecker.peek`, making off-by-one behavior important. ANSI styling must reset on state transitions.

## Test Signals
Existing nanorst tests should cover inline emphasis/code, bold, escaped markers, code blocks, directives, reference substitution and missing references, lazy conversion, terminal/non-terminal rendering, and invalid final states.
