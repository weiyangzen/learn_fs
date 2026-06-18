# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdts.h

Text state structure/API header for `pdfwrite`. It defines the client-visible text-state values and declares context transition, synchronization, positioning, and append helpers used across the text subsystem.

Key contents:
- Forward-declares `pdf_text_state_t`.
- Defines `pdf_text_state_values_t` with character spacing, active PDF font resource, font size, text-to-user/device matrix, render mode, and word spacing.
- Provides `TEXT_STATE_VALUES_DEFAULT`.
- Declares stream/string-to-text context transitions and closing the text aspect of current contents.
- Declares internal text helpers for render-mode stroke detection, reading text state values, setting WMode, setting text state values, transforming text-space distances, reading current text position, and appending characters with advance widths.

Notable dependencies:
- Includes `gsmatrix.h`.
- Comments point to `gdevpdtt.h` for coordinate-system discussion used by the broader text subsystem.
- Implemented by `gdevpdts.c` and consumed by simple/composite/bitmap text processing modules.

Research notes:
- The matrix comment is important: pdfwrite treats the text-space-to-user-space matrix as text-space-to-device-space for output purposes.
- The header separates caller-provided text-state values from the implementation's buffering/emission decisions.
- No filesystem behavior is present.
