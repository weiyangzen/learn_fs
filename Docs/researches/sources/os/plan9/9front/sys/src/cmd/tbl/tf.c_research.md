# File Research: sources/os/plan9/9front/sys/src/cmd/tbl/tf.c

Saves and restores troff fill state around generated tables.

Key points:
- `savefill` defines a macro that restores point size, vertical spacing, indentation, fill mode, and adjustment mode, then switches table output to no-fill mode.
- Initializes `#~`, an output-device-specific offset used for T450/nroff box adjustment.
- `rstofill` invokes the saved-state macro.
- `endoff` clears line-stop registers, removes text diversions, and emits `last`.
- `ifdivert` sets string `#d` to either `.d` or `nl` depending on diversion state.
- `saveline` and `restline` preserve input line accounting around table processing.
- `cleanfc` resets field characters with `.fc`.

Dependencies and interactions:
- Uses `linestop`, `texstr`, `texct`, `last`, `iline`, and `linstart`.
- Emitted macros are consumed by later row and line rendering code.

Research relevance:
- This file isolates table rendering from the surrounding document’s troff fill and line-count state.
